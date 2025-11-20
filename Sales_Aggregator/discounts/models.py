from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название категории',
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(
        verbose_name='Описание условий скидки',
    )
    place = models.CharField(
        max_length=200,
        verbose_name='Место (магазин, кафе и т.д.)',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Категория',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    @property
    def rating(self) -> int:
        upvotes: int = self.votes.filter(vote_type='up').count()
        downvotes: int = self.votes.filter(vote_type='down').count()
        return upvotes - downvotes

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title


class Vote(models.Model):
    VOTE_TYPES: list[tuple[str, str]] = [
        ('up', 'Положительная'),
        ('down', 'Отрицательная'),
    ]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Пост',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Пользователь',
    )
    vote_type = models.CharField(
        max_length=4,
        choices=VOTE_TYPES,
        verbose_name='Тип оценки',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оценки',
    )

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ['post', 'user']

    def __str__(self) -> str:
        return f'{self.user.username} - {self.vote_type} - {self.post.title}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Пост',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        unique_together = ['user', 'post']

    def __str__(self) -> str:
        return f'{self.user.username} - {self.post.title}'
