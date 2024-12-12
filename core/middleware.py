from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define public URLs that don't require authentication
        public_paths = [
            reverse('login'),
            '/admin/',
            settings.STATIC_URL,
            '/reset/',  # This covers all password reset URLs
            '/password_reset/',  # This covers initial password reset
        ]

        # Check if the user is not authenticated and the request is not for public URLs
        if not request.user.is_authenticated and \
           not any(request.path_info.startswith(path) for path in public_paths):
            return redirect('login')
        return self.get_response(request)