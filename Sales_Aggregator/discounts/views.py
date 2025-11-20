from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, QuerySet
from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

from .forms import PostForm
from .models import Category, Favorite, Post, Vote


def home(request: HttpRequest) -> HttpResponse:
    posts: QuerySet[Post] = Post.objects.annotate(
        upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
        downvotes_count=Count(
            'votes',
            filter=Q(votes__vote_type='down'),
        ),
    )

    category_filter: str | None = request.GET.get('category')
    if category_filter:
        posts = posts.filter(category_id=category_filter)

    sort_by: str = request.GET.get('sort', 'newest')
    if sort_by == 'rating':
        posts = posts.order_by(
            '-upvotes_count',
            'downvotes_count',
            '-created_at',
        )
    else:
        posts = posts.order_by('-created_at')

    categories: QuerySet[Category] = Category.objects.all()

    user_votes: dict[int, str] = {}
    user_favorites: set[int] = set()

    if request.user.is_authenticated:
        post_ids: list[int] = list(posts.values_list('id', flat=True))
        if post_ids:
            votes = Vote.objects.filter(
                post_id__in=post_ids,
                user=request.user,
            )
            for vote in votes:
                user_votes[vote.post_id] = vote.vote_type

            favorites = Favorite.objects.filter(
                post_id__in=post_ids,
                user=request.user,
            )
            user_favorites = {fav.post_id for fav in favorites}

    for post in posts:
        post.user_vote = user_votes.get(post.id)  # type: ignore[attr-defined]
        post.is_favorite = post.id in user_favorites  # type: ignore[attr-defined]

    context: dict[str, Any] = {
        'posts': posts,
        'categories': categories,
        'current_category': category_filter,
        'sort_by': sort_by,
    }

    return render(request, 'discounts/home.html', context)


@method_decorator(login_required, name='dispatch')
class CreatePostView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        form = PostForm()
        return render(request, 'discounts/create_post.html', {'form': form})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = PostForm(request.POST)
        if form.is_valid():
            post: Post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('home') + '?post_created=1')
        return render(request, 'discounts/create_post.html', {'form': form})


@login_required
@require_http_methods(['POST'])
def vote_post(
    request: HttpRequest,
    post_id: int,
    vote_type: str,
) -> HttpResponse:
    post: Post = get_object_or_404(Post, id=post_id)

    if vote_type not in ['up', 'down']:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {'error': 'Неверный тип оценки'},
                status=400,
            )
        messages.error(request, 'Неверный тип оценки')
        return redirect('home')

    existing_vote: Vote | None = Vote.objects.filter(
        post=post,
        user=request.user,
    ).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
            user_vote: str | None = None
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
            user_vote = vote_type
    else:
        Vote.objects.create(post=post, user=request.user, vote_type=vote_type)
        user_vote = vote_type

    upvotes_count: int = post.votes.filter(vote_type='up').count()
    downvotes_count: int = post.votes.filter(vote_type='down').count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {
                'success': True,
                'user_vote': user_vote,
                'upvotes_count': upvotes_count,
                'downvotes_count': downvotes_count,
            }
        )

    referer: str = request.META.get('HTTP_REFERER', '')
    if 'favorites' in referer:
        return redirect('favorites')
    if 'my-posts' in referer:
        return redirect('user_posts')
    return redirect('home')


@login_required
@require_http_methods(['POST'])
def toggle_favorite(request: HttpRequest, post_id: int) -> HttpResponse:
    post: Post = get_object_or_404(Post, id=post_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        post=post,
    )

    if not created:
        favorite.delete()
        is_favorite: bool = False
        message: str = 'Пост удален из избранного'
    else:
        is_favorite = True
        message = 'Пост добавлен в избранное'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {'success': True, 'is_favorite': is_favorite, 'message': message}
        )

    if not created:
        messages.info(request, message)
    else:
        messages.success(request, message)

    referer: str = request.META.get('HTTP_REFERER', '')
    if 'favorites' in referer:
        return redirect('favorites')
    if 'my-posts' in referer:
        return redirect('user_posts')
    return redirect('home')


@login_required
def user_posts(request: HttpRequest) -> HttpResponse:
    posts: QuerySet[Post] = (
        Post.objects.filter(author=request.user)
        .annotate(
            upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
            downvotes_count=Count(
                'votes',
                filter=Q(votes__vote_type='down'),
            ),
        )
        .order_by('-created_at')
    )

    user_votes: dict[int, str] = {}
    user_favorites: set[int] = set()

    post_ids: list[int] = list(posts.values_list('id', flat=True))
    if post_ids:
        votes = Vote.objects.filter(post_id__in=post_ids, user=request.user)
        for vote in votes:
            user_votes[vote.post_id] = vote.vote_type

        favorites = Favorite.objects.filter(
            post_id__in=post_ids,
            user=request.user,
        )
        user_favorites = {fav.post_id for fav in favorites}

    for post in posts:
        post.user_vote = user_votes.get(post.id)  # type: ignore[attr-defined]
        post.is_favorite = post.id in user_favorites  # type: ignore[attr-defined]

    return render(request, 'discounts/user_posts.html', {'posts': posts})


@login_required
@require_http_methods(['POST'])
def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    post: Post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    'error': 'У вас нет прав на удаление этого поста',
                },
                status=403,
            )
        messages.error(
            request,
            'У вас нет прав на удаление этого поста',
        )
        return redirect('user_posts')

    post.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(
            {'success': True, 'message': 'Пост успешно удален'}
        )

    messages.success(request, 'Пост успешно удален')
    return redirect('user_posts')


@login_required
def favorites(request: HttpRequest) -> HttpResponse:
    favorite_posts: QuerySet[Post] = (
        Post.objects.filter(favorited_by__user=request.user)
        .annotate(
            upvotes_count=Count('votes', filter=Q(votes__vote_type='up')),
            downvotes_count=Count(
                'votes',
                filter=Q(votes__vote_type='down'),
            ),
        )
        .order_by('-favorited_by__created_at')
    )

    user_votes: dict[int, str] = {}

    post_ids: list[int] = list(favorite_posts.values_list('id', flat=True))
    if post_ids:
        votes = Vote.objects.filter(post_id__in=post_ids, user=request.user)
        for vote in votes:
            user_votes[vote.post_id] = vote.vote_type

    for post in favorite_posts:
        post.user_vote = user_votes.get(post.id)  # type: ignore[attr-defined]
        post.is_favorite = True  # type: ignore[attr-defined]

    return render(
        request,
        'discounts/favorites.html',
        {'posts': favorite_posts},
    )
