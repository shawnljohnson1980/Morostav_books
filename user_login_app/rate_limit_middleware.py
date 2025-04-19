from django.http import HttpResponseTooManyRequests
from django.core.cache import cache
import time

class RateLimitMiddleware:
    RATE_LIMIT = 5        # Max requests
    TIME_WINDOW = 60      # In seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        key = f"rl:{ip}"
        request_times = cache.get(key, [])

        # Clean old timestamps
        now = time.time()
        request_times = [t for t in request_times if now - t < self.TIME_WINDOW]

        if len(request_times) >= self.RATE_LIMIT:
            return HttpResponseTooManyRequests("⛔ Slow down, cowboy. You’ve hit the limit.")

        request_times.append(now)
        cache.set(key, request_times, timeout=self.TIME_WINDOW)

        return self.get_response(request)

    def get_client_ip(self, request):
        return request.META.get('REMOTE_ADDR')
        