from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # extra_fields.setdefault('user_type', 'super_admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    # Add related_name to resolve the clash
    first_name = models.CharField(max_length=30, blank=True, verbose_name='Nombre')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='Apellido')
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_user_set',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_user_set',
        related_query_name='core_user',
    )
    
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.username} ({', '.join([group.name for group in self.groups.all()])})"
    
class UserPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    key = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        unique_together = ('user', 'key')

    def __str__(self):
        return f"{self.user.username} - {self.key}"
    
    
def create_user_type_groups():
    user_types = ['super_admin', 'owner', '	assistant', 'doctor']
    for user_type in user_types:
        Group.objects.get_or_create(name=user_type)        