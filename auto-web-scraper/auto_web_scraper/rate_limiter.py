"""
速率限制模块
控制请求间隔，避免被封禁
"""
import time
import random
import threading
from typing import Optional
from collections import deque


class RateLimiter:
    """
    速率限制器
    支持固定间隔、随机间隔、滑动窗口等多种速率限制策略
    """

    def __init__(
        self,
        min_delay: float = 1.0,
        max_delay: float = 3.0,
        random_delay: bool = True,
        concurrency: int = 1,
        requests_per_minute: Optional[int] = None,
    ):
        """
        初始化速率限制器

        Args:
            min_delay: 最小延迟(秒)
            max_delay: 最大延迟(秒)
            random_delay: 是否使用随机延迟
            concurrency: 并发数
            requests_per_minute: 每分钟最大请求数
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.random_delay = random_delay
        self.concurrency = concurrency
        self.requests_per_minute = requests_per_minute

        self._lock = threading.Lock()
        self._last_request_time = 0.0
        self._request_times: deque = deque(maxlen=1000)
        self._active_requests = 0

    def wait(self):
        """
        等待，直到可以发送下一个请求
        """
        with self._lock:
            while self._active_requests >= self.concurrency:
                time.sleep(0.1)

            now = time.time()
            elapsed = now - self._last_request_time

            if self.requests_per_minute is not None:
                while len(self._request_times) > 0:
                    earliest = self._request_times[0]
                    if now - earliest <= 60:
                        break
                    self._request_times.popleft()

                if len(self._request_times) >= self.requests_per_minute:
                    wait_time = 60 - (now - self._request_times[0])
                    if wait_time > 0:
                        time.sleep(wait_time)
                        now = time.time()

            delay = self._calculate_delay()
            if elapsed < delay:
                sleep_time = delay - elapsed
                time.sleep(sleep_time)

            self._last_request_time = time.time()
            self._request_times.append(self._last_request_time)
            self._active_requests += 1

    def release(self):
        """
        释放请求槽位
        """
        with self._lock:
            if self._active_requests > 0:
                self._active_requests -= 1

    def _calculate_delay(self) -> float:
        """
        计算延迟时间

        Returns:
            延迟时间(秒)
        """
        if self.random_delay:
            return random.uniform(self.min_delay, self.max_delay)
        else:
            return self.min_delay

    def __enter__(self):
        """
        上下文管理器入口
        """
        self.wait()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        """
        self.release()
        return False

    def get_stats(self) -> dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        with self._lock:
            return {
                "min_delay": self.min_delay,
                "max_delay": self.max_delay,
                "random_delay": self.random_delay,
                "concurrency": self.concurrency,
                "requests_per_minute": self.requests_per_minute,
                "last_request_time": self._last_request_time,
                "active_requests": self._active_requests,
                "requests_in_window": len(self._request_times),
            }

    def update_config(
        self,
        min_delay: Optional[float] = None,
        max_delay: Optional[float] = None,
        random_delay: Optional[bool] = None,
        concurrency: Optional[int] = None,
        requests_per_minute: Optional[int] = None,
    ):
        """
        更新配置

        Args:
            min_delay: 最小延迟(秒)
            max_delay: 最大延迟(秒)
            random_delay: 是否使用随机延迟
            concurrency: 并发数
            requests_per_minute: 每分钟最大请求数
        """
        with self._lock:
            if min_delay is not None:
                self.min_delay = min_delay
            if max_delay is not None:
                self.max_delay = max_delay
            if random_delay is not None:
                self.random_delay = random_delay
            if concurrency is not None:
                self.concurrency = concurrency
            if requests_per_minute is not None:
                self.requests_per_minute = requests_per_minute
