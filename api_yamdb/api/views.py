import jwt

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import (
    filters,
    permissions,
    status,
    viewsets
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import ParseError

from .filters import TitleFilter
from .methods import get_user_role
from .permissions import (
    IsAdminOrReadOnly,
    IsAdminUserCustom,
)

from .serializers import (
    CategorySerializer,
    CustomUserSerializer,
    GenreSerializer,
    MyTokenObtainSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    CommentSerializer
)

from api_yamdb.settings import SECRET_KEY
from .mixins import ListDestroyCreateViewSet
from reviews.models import Category, Genre, Title, CustomUser, Review


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'username'
    trailing_slash = '/'

    def get_permissions(self):
        if 'getme' in self.action_map.values():
            return (permissions.IsAuthenticated(),)
        if self.suffix == 'users-list' or 'user-detail':
            return (IsAdminUserCustom(),)

    @action(detail=True, url_path='me', methods=['get', 'patch'])
    def getme(self, request):
        request_user = request.user
        custom_user = CustomUser.objects.get(username=request_user.username)
        if request.method == 'GET':
            serializer = self.get_serializer(custom_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            rd = request.data.copy()
            if 'role' in rd:
                del rd['role']
            if 'username' not in rd:
                rd['username'] = request_user.username
            if 'email' not in rd:
                rd['email'] = request_user.email
            serializer = self.get_serializer(custom_user, data=rd)
            if serializer.is_valid():
                serializer.save()
                if 'email' in rd or 'username' in rd:
                    return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        rd = self.request.data
        role = rd.get('role')
        if role == 'admin':
            is_staff = True
        else:
            is_staff = False
        serializer.save(is_staff=is_staff)

    def perform_update(self, serializer):
        rd = self.request.data
        role = rd.get('role')
        if role == 'admin':
            is_staff = True
        else:
            is_staff = False
        serializer.save(is_staff=is_staff)


class APISignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_active=False)
            user = serializer.instance
            rd = request.data
            username = rd.get('username')
            email = rd.get('email')
            confirmation_code = user.confirmation_code
            mail_theme = 'Подтверждение регистрации пользователя'
            mail_text = (
                f'Здравствуйте!\n\n\tВы (или кто-то другой) '
                'запросили регистрацию на сайте YaMDB. '
                'Для подтверждения регистрации отправьте POST запрос '
                'на адрес: http://127.0.0.1/api/v1/auth/token/. '
                f'В теле запроса передайте имя пользователя {username} '
                f'по ключу "username" и код \n\n{confirmation_code}\n\n'
                f'по ключу "confirmation_code".'
            )
            mail_from = 'haus.esc@gmail.com'
            mail_to = [email]
            send_mail(
                mail_theme,
                mail_text,
                mail_from,
                mail_to,
                fail_silently=False
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        rd = request.data.copy()
        serializer = MyTokenObtainSerializer(data=rd)
        if serializer.is_valid():
            username = rd.get('username')
            user = get_object_or_404(CustomUser, username=username)
            user.is_active = True
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(ListDestroyCreateViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(ListDestroyCreateViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_class = TitleFilter
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        if self.get_title().reviews.filter(
            author__username=self.request.user
        ).exists():
            raise ParseError(
                detail='Повторный отзыв запрещен!'
            )
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
