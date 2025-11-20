from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    created_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username
    