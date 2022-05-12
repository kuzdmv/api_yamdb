import jwt

from api.methods import text_processor

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import SECRET_KEY
from .validators import validate_year

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class CustomUserManager(BaseUserManager):
    def create_superuser(self, username, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                '"is_staff" суперпользователя должно быть в режиме "True"'
            )
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                '"is_superuser" суперпользователя должно быть в режиме "True"'
            )
        if 'role' in other_fields:
            role = other_fields.get('role')
            del other_fields['role']
        else:
            role = 'admin'

        return self.create_user(
            username,
            email,
            role,
            password,
            **other_fields
        )

    def create_user(
        self,
        username,
        email,
        role='user',
        password=None,
        **other_fields
    ):
        if not email:
            raise ValueError('Необходимо указать email')
        if not username:
            raise ValueError('Необходимо указать username')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            role=role,
            **other_fields
        )
        if role == 'admin':
            user.is_staff = True
            user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        choices=ROLE_CHOICES,
        default='user',
        max_length=16
    )
    email = models.EmailField('E-MAIL', unique=True, blank=False, null=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[mM][eE]$',
                message=(
                    'Попытка регистрации пользователя '
                    'под me-образным именем'
                ),
                inverse_match=True
            ),
        ),
    )

    objects = CustomUserManager()

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}, уровень доступа: {self.role}'

    @property
    def token(self):
        token = AccessToken.for_user(self)
        token['role'] = self.role
        token['is_superuser'] = self.is_superuser
        return token

    @property
    def confirmation_code(self):
        dict = {
            'username': self.username,
            'email': self.email
        }
        confirmation_code = jwt.encode(
            dict,
            SECRET_KEY,
            'HS256'
        )
        return confirmation_code


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['slug']


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['slug']


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(validators=[validate_year])
    description = models.CharField(max_length=200, blank=True,  null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='category',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['year']


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведения',
        null=True
    )
    text = models.TextField(
        max_length=200,
        verbose_name='Текст отзыва'
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)),
        error_messages={'validators': 'Укажите оценку от 1 до 10'},
        verbose_name='Оценка',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
        null=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Данная команда не даст повторно голосовать
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique_review'
            )]

    def __str__(self):
        return text_processor(self.text, 1)


class Comment(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, null=True,
        related_name='comments', verbose_name='Произведение'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        null=True
    )
    text = models.TextField('Текст комментария', max_length=200)
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, null=True
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return text_processor(self.text, 1)