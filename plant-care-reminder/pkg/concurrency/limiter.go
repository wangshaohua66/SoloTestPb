package concurrency

import (
	"context"
	"fmt"
	"sync"
	"time"

	"plant-care-reminder/config"
)

type Limiter struct {
	sem        chan struct{}
	timeout    time.Duration
	mu         sync.RWMutex
	maxReq     int
}

type Lock struct {
	mu sync.RWMutex
}

type KeyLock struct {
	locks sync.Map
}

var (
	globalLimiter *Limiter
	keyLock       *KeyLock
	once          sync.Once
)

func Init() {
	once.Do(func() {
		cfg := config.Get()
		maxReq := cfg.Concurrency.MaxRequests
		if maxReq <= 0 {
			maxReq = 100
		}
		timeout := time.Duration(cfg.Concurrency.TimeoutSeconds) * time.Second
		if timeout <= 0 {
			timeout = 30 * time.Second
		}
		globalLimiter = &Limiter{
			sem:     make(chan struct{}, maxReq),
			timeout: timeout,
			maxReq:  maxReq,
		}
		keyLock = &KeyLock{}
	})
}

func GetLimiter() *Limiter {
	return globalLimiter
}

func GetKeyLock() *KeyLock {
	return keyLock
}

func (l *Limiter) Acquire(ctx context.Context) error {
	select {
	case l.sem <- struct{}{}:
		return nil
	case <-ctx.Done():
		return fmt.Errorf("context cancelled while acquiring limiter: %w", ctx.Err())
	case <-time.After(l.timeout):
		return fmt.Errorf("timeout waiting for request slot, max concurrent requests: %d", l.maxReq)
	}
}

func (l *Limiter) Release() {
	select {
	case <-l.sem:
	default:
	}
}

func (l *Limiter) WithLimit(ctx context.Context, fn func() error) error {
	if err := l.Acquire(ctx); err != nil {
		return err
	}
	defer l.Release()
	
	done := make(chan error, 1)
	go func() {
		defer func() {
			if r := recover(); r != nil {
				done <- fmt.Errorf("panic recovered: %v", r)
			}
		}()
		done <- fn()
	}()

	select {
	case err := <-done:
		return err
	case <-ctx.Done():
		return fmt.Errorf("operation cancelled: %w", ctx.Err())
	case <-time.After(l.timeout):
		return fmt.Errorf("operation timed out after %v", l.timeout)
	}
}

func (l *Limiter) Current() int {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return len(l.sem)
}

func (l *Limiter) Max() int {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return l.maxReq
}

func (l *Lock) WithWrite(fn func() error) error {
	l.mu.Lock()
	defer l.mu.Unlock()
	return fn()
}

func (l *Lock) WithRead(fn func() error) error {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return fn()
}

func (kl *KeyLock) getLock(key string) *sync.RWMutex {
	actual, _ := kl.locks.LoadOrStore(key, &sync.RWMutex{})
	return actual.(*sync.RWMutex)
}

func (kl *KeyLock) WithWrite(key string, fn func() error) error {
	lock := kl.getLock(key)
	lock.Lock()
	defer lock.Unlock()
	return fn()
}

func (kl *KeyLock) WithRead(key string, fn func() error) error {
	lock := kl.getLock(key)
	lock.RLock()
	defer lock.RUnlock()
	return fn()
}
