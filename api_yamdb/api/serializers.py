from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Genre, Title, GenreTitle


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
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)
        if 'category' in data:
            cat_slug = data.get('category')
            try:
                category = Category.objects.get(slug=cat_slug)
            except Category.DoesNotExist:
                raise ValidationError(
                    {'category': ['Такой категории нет']},
                    code='invalid',
                )
            internal_data['category'] = category
        if 'genre' in data:
            genre_slugs = data.get('genre')
            genres = []
            for genre_slug in genre_slugs:
                try:
                    genre = Genre.objects.get(slug=genre_slug)
                except Genre.DoesNotExist:
                    raise ValidationError(
                        {'genre': ['Такого жанра нет']},
                        code='invalid',
                    )
                genres.append(genre)
            internal_data['genre'] = genres
        return internal_data

    def create(self, validated_data):
        if 'category' not in validated_data:
            raise ValidationError(
                {'category': ['Обязательно необходимо указать категорию']},
                code='invalid',
            )
        if 'genre' not in validated_data:
            raise ValidationError(
                {'genre': ['Обязательно необходимо указать жанр']},
                code='invalid',
            )
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(title=title, genre=genre)
        return title

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
