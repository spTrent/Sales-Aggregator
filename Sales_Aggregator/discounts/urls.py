from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.CreatePostView.as_view(), name='create_post'),
    path('vote/<int:post_id>/<str:vote_type>/', views.vote_post, name='vote_post'),
    path('favorite/<int:post_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('my-posts/', views.user_posts, name='user_posts'),
    path('favorites/', views.favorites, name='favorites'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
]