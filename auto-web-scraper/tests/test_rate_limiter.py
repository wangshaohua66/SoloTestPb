"""
速率限制模块单元测试
"""
import pytest
import time

from auto_web_scraper.rate_limiter import RateLimiter


class TestRateLimiter:
    """
    速率限制器测试类
    """

    def test_init_defaults(self):
        """
        测试默认初始化
        """
        limiter = RateLimiter()

        assert limiter.min_delay == 1.0
        assert limiter.max_delay == 3.0
        assert limiter.random_delay is True
        assert limiter.concurrency == 1
        assert limiter.requests_per_minute is None

    def test_init_custom(self):
        """
        测试自定义初始化
        """
        limiter = RateLimiter(
            min_delay=0.5,
            max_delay=2.0,
            random_delay=False,
            concurrency=5,
            requests_per_minute=60,
        )

        assert limiter.min_delay == 0.5
        assert limiter.max_delay == 2.0
        assert limiter.random_delay is False
        assert limiter.concurrency == 5
        assert limiter.requests_per_minute == 60

    def test_context_manager(self):
        """
        测试上下文管理器
        """
        limiter = RateLimiter(min_delay=0.1, max_delay=0.2, random_delay=False)

        start = time.time()
        with limiter:
            pass
        elapsed1 = time.time() - start

        start = time.time()
        with limiter:
            pass
        elapsed2 = time.time() - start

        assert elapsed2 >= 0.05

    def test_calculate_delay_random(self):
        """
        测试计算随机延迟
        """
        limiter = RateLimiter(min_delay=1.0, max_delay=2.0, random_delay=True)

        delays = [limiter._calculate_delay() for _ in range(10)]
        for d in delays:
            assert 1.0 <= d <= 2.0

    def test_calculate_delay_fixed(self):
        """
        测试计算固定延迟
        """
        limiter = RateLimiter(min_delay=1.5, max_delay=2.0, random_delay=False)

        delays = [limiter._calculate_delay() for _ in range(5)]
        assert all(d == 1.5 for d in delays)

    def test_get_stats(self):
        """
        测试获取统计信息
        """
        limiter = RateLimiter(min_delay=0.1)

        stats = limiter.get_stats()

        assert "min_delay" in stats
        assert "max_delay" in stats
        assert "random_delay" in stats
        assert "concurrency" in stats
        assert "requests_per_minute" in stats
        assert "active_requests" in stats

    def test_update_config(self):
        """
        测试更新配置
        """
        limiter = RateLimiter()

        limiter.update_config(
            min_delay=0.5,
            max_delay=1.0,
            random_delay=False,
            concurrency=3,
            requests_per_minute=30,
        )

        assert limiter.min_delay == 0.5
        assert limiter.max_delay == 1.0
        assert limiter.random_delay is False
        assert limiter.concurrency == 3
        assert limiter.requests_per_minute == 30

    def test_wait_and_release(self):
        """
        测试等待和释放
        """
        limiter = RateLimiter(min_delay=0.1, max_delay=0.1, random_delay=False)

        limiter.wait()
        assert limiter._active_requests == 1

        limiter.release()
        assert limiter._active_requests == 0
