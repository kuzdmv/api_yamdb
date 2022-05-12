import re
import jwt

from api_yamdb.settings import SECRET_KEY
from jwt.exceptions import DecodeError

from rest_framework import exceptions, serializers
from rest_framework.relations import SlugRelatedField

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
    genre = GenreAndCategorySlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = GenreAndCategorySlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        sum_rating = None
        reviews = Review.objects.filter(title=obj.id)
        if reviews:
            count = reviews.count()
            for review in reviews:
                sum_rating = 0
                sum_rating += review.score
                return int(sum_rating / count)
        return sum_rating

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Review
        exclude = ('title',)
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        exclude = ('review',)
        read_only_fields = ('review',)
