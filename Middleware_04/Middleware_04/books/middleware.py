import logging
from django.http import HttpResponse
from django.utils.timezone import now
import uuid
from django.http import HttpResponse
from collections import defaultdict
from time import time

# Configure logging
logging.basicConfig(
    filename='request_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log request details
        logging.info(
            f"Request: {request.method} {request.get_full_path()} at {now()} IP: {request.META.get('REMOTE_ADDR')}"
        )

        # Process the request
        response = self.get_response(request)

        # Log response status
        logging.info(
            f"Response: Status {response.status_code} for {request.get_full_path()}"
        )
        return response

    def process_exception(self, request, exception):
        logging.error(f"Exception: {str(exception)} for {request.get_full_path()}")
        return HttpResponse("Internal Server Error", status=500)


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check authentication for specific URLs
        protected_paths = ['/books/', '/books/add-review/']
        if (
            any(request.path.startswith(path) for path in protected_paths)
            and not request.user.is_authenticated
        ):
            return HttpResponse("Unauthorized", status=401)

        return self.get_response(request)


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        response = self.get_response(request)
        response['X-Request-ID'] = request_id
        return response


class APIVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-API-Version'] = '1.0'
        return response


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = defaultdict(list)
        self.limit = 10  # 10 requests per minute
        self.window = 60  # 1 minute

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        now = time()
        self.requests[ip] = [t for t in self.requests[ip] if now - t < self.window]

        if len(self.requests[ip]) >= self.limit:
            return HttpResponse("Rate limit exceeded", status=429)

        self.requests[ip].append(now)
        return self.get_response(request)


class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time()
        response = self.get_response(request)
        duration = time() - start_time
        logging.info(
            f"Request took {duration:.3f} seconds for {request.get_full_path()}"
        )
        return response
