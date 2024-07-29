from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth import logout, update_session_auth_hash
from django.urls import reverse_lazy
from .models import User, UserPreference
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from .forms import UserForm, UserProfileForm, CustomPasswordChangeForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    def get_success_url(self):
        # return reverse_lazy('home')  # Redirect to home after login
        return reverse_lazy('patient_list')

class CustomLogoutView(LogoutView):
    template_name = 'core/logout.html'
    next_page = reverse_lazy('login')
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        logout(request)
        return render(request, self.template_name)

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'
    login_url = 'login'  # This specifies where to redirect if the user is not logged in


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'user/user_list.html'
    context_object_name = 'users'
    permission_required = 'core.view_user'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.all()
        try:
            superadmin_group = Group.objects.get(name='superadmin')
            queryset = queryset.exclude(groups=superadmin_group)
        except Group.DoesNotExist:
            # If the 'superadmin' group doesn't exist, we don't need to exclude any users
            pass
        return queryset.order_by('username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginate_by = self.request.GET.get('paginate_by', self.paginate_by)
        paginator = Paginator(self.get_queryset(), paginate_by)
        page = self.request.GET.get('page')
        users = paginator.get_page(page)
        context['users'] = users
        context['paginate_by'] = int(paginate_by)
        return context

class UserDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = User
    template_name = 'user/user_detail.html'
    permission_required = 'core.view_user'

class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'user/user_form.html'
    success_url = reverse_lazy('user_list')
    permission_required = 'core.add_user'

class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'user/user_form.html'
    success_url = reverse_lazy('user_list')
    permission_required = 'core.change_user'

    def form_valid(self, form):
        # If the password field is empty, remove it from the form
        # to prevent overwriting with an empty string
        if not form.cleaned_data.get('password'):
            del form.cleaned_data['password']
        return super().form_valid(form)

class UserDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'user/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')
    permission_required = 'core.delete_user'
    
@method_decorator(ensure_csrf_cookie, name='dispatch')
class UserPreferenceView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        preference_key = request.GET.get('key')
        if not preference_key:
            return JsonResponse({'error': 'No key provided'}, status=400)
        
        try:
            preference = UserPreference.objects.get(user=request.user, key=preference_key)
            return JsonResponse({'value': preference.value})
        except UserPreference.DoesNotExist:
            return JsonResponse({'value': None})

    def post(self, request, *args, **kwargs):
        preference_key = request.POST.get('key')
        preference_value = request.POST.get('value')
        
        if not preference_key or not preference_value:
            return JsonResponse({'error': 'Both key and value are required'}, status=400)
        
        UserPreference.objects.update_or_create(
            user=request.user,
            key=preference_key,
            defaults={'value': preference_value}
        )
        return JsonResponse({'status': 'success'})
    
class UserProfileView(LoginRequiredMixin, View):
    template_name = 'user/user_profile.html'

    def get(self, request):
        user_form = UserProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'user_form': user_form,
            'password_form': password_form
        })

    def post(self, request):
        if 'update_profile' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, _('Su perfil ha sido actualizado.'))
            password_form = CustomPasswordChangeForm(user=request.user)
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, _('Su contraseña ha sido actualizada.'))
            user_form = UserProfileForm(instance=request.user)
        else:
            user_form = UserProfileForm(instance=request.user)
            password_form = CustomPasswordChangeForm(user=request.user)
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'password_form': password_form
        })