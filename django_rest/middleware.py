from django.http import HttpResponseForbidden
from django.urls import reverse

class RestrictAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        swagger_urls = [
            reverse('schema-redoc'),
            reverse('schema-swagger-ui'),
            reverse('schema-json'),
        ]

        api_urls = [
            '/api/',
            '/admin/',
        ]

        if request.path in swagger_urls or any(request.path.startswith(url) for url in api_urls):
            return self.get_response(request)

        return HttpResponseForbidden("Access denied. Only Swagger is allowed.")
