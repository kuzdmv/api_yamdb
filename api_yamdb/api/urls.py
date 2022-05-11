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
  
  

router_v1_a = CustomRouter()
router_v1_a.register('users', UserViewSet)
router_v1_b = routers.DefaultRouter()
router_v1_b.register('categories', CategoryViewSet, basename='categories')
router_v1_b.register('genres', GenreViewSet, basename='genres')
router_v1_b.register('titles', TitleViewSet, basename='titles')
router_v1_b.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                     basename='review')
router_v1_b.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', APISignupView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
]

