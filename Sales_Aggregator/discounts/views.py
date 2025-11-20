from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
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

    user_votes = {}
    user_favorites = set()
    
    if request.user.is_authenticated:
        post_ids = list(posts.values_list('id', flat=True))
        if post_ids:
            votes = Vote.objects.filter(post_id__in=post_ids, user=request.user)
            for vote in votes:
                user_votes[vote.post_id] = vote.vote_type
            favorites = Favorite.objects.filter(post_id__in=post_ids, user=request.user)
            user_favorites = {fav.post_id for fav in favorites}

    for post in posts:
        post.user_vote = user_votes.get(post.id)
        post.is_favorite = post.id in user_favorites
    
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
            return redirect(reverse('home') + '?post_created=1')
        return render(request, 'discounts/create_post.html', {'form': form})

@login_required
@require_http_methods(["POST"])
def vote_post(request, post_id, vote_type):
    post = get_object_or_404(Post, id=post_id)
    
    if vote_type not in ['up', 'down']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Неверный тип оценки'}, status=400)
        messages.error(request, 'Неверный тип оценки')
        return redirect('home')

    existing_vote = Vote.objects.filter(post=post, user=request.user).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
            user_vote = None
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
            user_vote = vote_type
    else:
        Vote.objects.create(post=post, user=request.user, vote_type=vote_type)
        user_vote = vote_type

    upvotes_count = post.votes.filter(vote_type='up').count()
    downvotes_count = post.votes.filter(vote_type='down').count()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'user_vote': user_vote,
            'upvotes_count': upvotes_count,
            'downvotes_count': downvotes_count
        })
    
    referer = request.META.get('HTTP_REFERER', '')
    if 'favorites' in referer:
        return redirect('favorites')
    elif 'my-posts' in referer:
        return redirect('user_posts')
    
    return redirect('home')

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        post=post
    )
    
    if not created:
        favorite.delete()
        is_favorite = False
        message = 'Пост удален из избранного'
    else:
        is_favorite = True
        message = 'Пост добавлен в избранное'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
    
    if not created:
        messages.info(request, message)
    else:
        messages.success(request, message)
    
    referer = request.META.get('HTTP_REFERER', '')
    if 'favorites' in referer:
        return redirect('favorites')
    elif 'my-posts' in referer:
        return redirect('user_posts')
    
    return redirect('home')

@login_required
def user_posts(request):
    posts = Post.objects.filter(author=request.user).annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
        downvotes_count=Count('votes', filter=Q(votes__vote_type='down'))
    ).order_by('-created_at')
    
    user_votes = {}
    user_favorites = set()
    post_ids = list(posts.values_list('id', flat=True))
    if post_ids:
        votes = Vote.objects.filter(post_id__in=post_ids, user=request.user)
        for vote in votes:
            user_votes[vote.post_id] = vote.vote_type
        
        favorites = Favorite.objects.filter(post_id__in=post_ids, user=request.user)
        user_favorites = {fav.post_id for fav in favorites}
    
    for post in posts:
        post.user_vote = user_votes.get(post.id)
        post.is_favorite = post.id in user_favorites
    
    return render(request, 'discounts/user_posts.html', {'posts': posts})

@login_required
@require_http_methods(["POST"])
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'У вас нет прав на удаление этого поста'}, status=403)
        messages.error(request, 'У вас нет прав на удаление этого поста')
        return redirect('user_posts')
    
    post.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Пост успешно удален'})
    
    messages.success(request, 'Пост успешно удален')
    return redirect('user_posts')

@login_required
def favorites(request):
    favorite_posts = Post.objects.filter(favorited_by__user=request.user).annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
        downvotes_count=Count('votes', filter=Q(votes__vote_type='down'))
    ).order_by('-favorited_by__created_at')
    
    user_votes = {}
    post_ids = list(favorite_posts.values_list('id', flat=True))
    if post_ids:
        votes = Vote.objects.filter(post_id__in=post_ids, user=request.user)
        for vote in votes:
            user_votes[vote.post_id] = vote.vote_type
    
    for post in favorite_posts:
        post.user_vote = user_votes.get(post.id)
        post.is_favorite = True  # Все посты на странице избранного уже в избранном
    
    return render(request, 'discounts/favorites.html', {'posts': favorite_posts})