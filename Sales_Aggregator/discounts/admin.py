from django.contrib import admin
from .models import Category, Post, Vote, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'place', 'created_at', 'rating']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description', 'place']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']