from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.views import View
from django.utils.decorators import method_decorator
from .models import Post, Category, Vote, Favorite
from .forms import PostForm

def home(request):
    posts = Post.objects.annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
        downvotes_count=Count('votes', filter=Q(votes__vote_type='down')) #аннотации для рейтинга
    )
    
    # Фильтрация по категориям
    category_filter = request.GET.get('category')
    if category_filter:
        posts = posts.filter(category_id=category_filter)
    
    # Сортировка
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'rating':
        posts = posts.order_by('-upvotes_count', 'downvotes_count', '-created_at')
    else:
        posts = posts.order_by('-created_at')

    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'current_category': category_filter,
        'sort_by': sort_by,
    }
    return render(request, 'discounts/home.html', context)

@method_decorator(login_required, name='dispatch')
class CreatePostView(View):
    def get(self, request):
        form = PostForm()
        return render(request, 'discounts/create_post.html', {'form': form})
    
    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, 'Пост о скидке успешно создан!')
            return redirect('home')
        return render(request, 'discounts/create_post.html', {'form': form})

@login_required
def vote_post(request, post_id, vote_type):
    post = get_object_or_404(Post, id=post_id)
    
    if vote_type not in ['up', 'down']:
        messages.error(request, 'Неверный тип оценки')
        return redirect('home')

    existing_vote = Vote.objects.filter(post=post, user=request.user).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        Vote.objects.create(post=post, user=request.user, vote_type=vote_type)
    
    return redirect('home')

@login_required
def toggle_favorite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if not created:
        favorite.delete()
        messages.info(request, 'Пост удален из избранного')
    else:
        messages.success(request, 'Пост добавлен в избранное')
    
    return redirect('home')

@login_required
def user_posts(request):
    posts = Post.objects.filter(author=request.user).annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
        downvotes_count=Count('votes', filter=Q(votes__vote_type='down'))
    ).order_by('-created_at')
    return render(request, 'discounts/user_posts.html', {'posts': posts})

@login_required
def favorites(request):
    favorite_posts = Post.objects.filter(favorited_by__user=request.user).annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
        downvotes_count=Count('votes', filter=Q(votes__vote_type='down'))
    ).order_by('-favorited_by__created_at')
    return render(request, 'discounts/favorites.html', {'posts': favorite_posts})