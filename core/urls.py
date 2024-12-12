from django.urls import path, reverse_lazy
from .views import CustomLoginView, CustomLogoutView, HomeView
from django.contrib.auth import views as auth_views
from .views import UserListView, UserDetailView, UserCreateView, UserUpdateView, UserDeleteView, UserProfileView, UserPreferenceView, UserResetPasswordView
from .forms import CustomSetPasswordForm


urlpatterns = [
    # Auth URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='user/password_reset_confirm.html',
            success_url=reverse_lazy('login'),
            form_class=CustomSetPasswordForm
        ),
        name='password_reset_confirm'
    ),
    
    # User Management URLs
    path('', HomeView.as_view(), name='home'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/reset-password/', UserResetPasswordView.as_view(), name='reset_user_password'),
    
    # Preferences
    path('user-preference/', UserPreferenceView.as_view(), name='user_preference'),
]