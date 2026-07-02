import asyncio
import time

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            while True:
                now = time.monotonic()
                # Filter calls within the period window
                self.calls = [t for t in self.calls if now - t < self.period]
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    break
                # Sleep until the oldest call falls outside the window
                sleep_time = self.period - (now - self.calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
