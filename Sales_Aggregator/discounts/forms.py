from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'place', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Скидка 20% на пиццу'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Опишите условия скидки, срок действия, требования...'
            }),
            'place': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название магазина, кафе, сервиса'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Заголовок скидки',
            'description': 'Описание условий',
            'place': 'Место',
            'category': 'Категория',
        }