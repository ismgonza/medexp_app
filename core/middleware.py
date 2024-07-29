from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and request.path_info != reverse('login') and not request.path_info.startswith('/admin/'):
            return redirect('login')
        return self.get_response(request)