from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='название')
    slug = models.SlugField(unique=True, verbose_name='урл')
    description = models.TextField(verbose_name='описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Здесь текст поста')
    pub_date = models.DateTimeField('date published', auto_now_add=True,
                                    verbose_name='опубликовано')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', verbose_name='автор')
    group = models.ForeignKey(Group, verbose_name='Группа',
                              on_delete=models.SET_NULL,
                              related_name='posts', blank=True, null=True,
                              help_text='Здесь группа')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='фото')

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments', verbose_name='автор')
    text = models.TextField('Текст комментария', verbose_name='текст',
                            help_text='Здесь текст комментария')
    created = models.DateTimeField('Дата создания', auto_now_add=True,
                                   verbose_name='создано')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='пользователь')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow')]
