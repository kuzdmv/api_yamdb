import re

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from jwt.exceptions import DecodeError
from rest_framework import exceptions, serializers

from .methods import decode
from reviews.models import (
    Category,
    Genre,
    Title,
    ROLE_CHOICES,
    CustomUser,
    Review,
    Comment
)


class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=ROLE_CHOICES, default='user'
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role')


class SignUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email'
        )

    def validate_username(self, value):
        user = None
        try:
            user = CustomUser.objects.get(username=value)
        except CustomUser.DoesNotExist:
            pass
        if user is not None:
            raise serializers.ValidationError(
                'У нас уже есть пользователь с таким username.'
            )
        match = re.fullmatch(r'^[mM][eE]$', value)
        if match:
            raise serializers.ValidationError('Недопустимое имя пользователя.')
        return value

    def validate_email(self, value):
        user = None
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            pass
        if user is not None:
            raise serializers.ValidationError(
                ('У нас уже есть пользователь с таким email.')
            )
        return value


class MyTokenObtainSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        ind = self.initial_data
        if 'username' not in ind:
            raise exceptions.ParseError(
                'В запросе отсутствует поле "username".'
            )
        username_from_query = ind.get('username')
        if CustomUser.objects.filter(username=username_from_query).exists():
            user_object = CustomUser.objects.get(username=username_from_query)
        else:
            raise exceptions.NotFound(
                (f'Пользователь с именем {username_from_query} '
                 'не найден в базе данных.')
            )
        if 'confirmation_code' not in ind:
            raise exceptions.ParseError(
                'В запросе отсутствует поле "confirmation_code".'
            )
        confirmation_code = ind.get('confirmation_code')
        try:
            payload = decode(confirmation_code)
        except DecodeError:
            raise exceptions.ParseError(
                'Данный код сфабрикован.'
            )
        email_from_code = payload.get('email')
        username_from_code = payload.get('username')
        email_from_model = user_object.email
        if username_from_code != username_from_query:
            raise exceptions.ParseError(
                'Похоже на подложный код подтверждения. '
                'Либо Вы сейчас указали не то имя пользователя, '
                'которое указали при получении кода подтверждения.'
            )
        if email_from_code != email_from_model:
            raise exceptions.ParseError(
                'Похоже на подложный код подтверждения.'
            )
        if user_object:
            token = user_object.token
            data = {'token': token}
            return data
        raise serializers.ValidationError(
            ('Пользователь, обратившийся за токеном, '
             'отсутствует в базе данных')
        )

    def create(self, validated_data):
        if 'email' in self.initial_data:
            pass
        if 'confirmation_code' in self.initial_data:
            pass


class GenreAndCategorySlugRelatedField(serializers.SlugRelatedField):
    def to_representation(self, obj):
        return {'name': obj.name, 'slug': obj.slug}


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        required=False,
    )
    text = serializers.CharField(allow_blank=True, required=True)

    class Meta:
        fields = ('id', 'text', 'score', 'author', 'pub_date', 'title')
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Можно оставлять не более одного отзыва!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date', 'review')
        model = Comment
