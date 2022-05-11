from django.urls import include, path
from rest_framework import routers

from .views import (
    APISignupView,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    TokenView,
    UserViewSet,
)

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')  
router.register('titles', TitleViewSet, basename='titles')  
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='review'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)
router.register('users', UserViewSet)  

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignupView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
]
