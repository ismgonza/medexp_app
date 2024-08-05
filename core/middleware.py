from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is not authenticated and the request is not for login, admin, or static files
        if not request.user.is_authenticated and \
           request.path_info != reverse('login') and \
           not request.path_info.startswith('/admin/') and \
           not request.path_info.startswith(settings.STATIC_URL):
            return redirect('login')
        return self.get_response(request)