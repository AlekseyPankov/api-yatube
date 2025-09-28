from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import APIComments, APICommentsDetail, GroupViewSet, PostViewSet

app_name = 'api'

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('groups', GroupViewSet)

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token),
    path('', include(router.urls)),
    path('posts/<int:post_pk>/comments/', APIComments.as_view()),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/',
         APICommentsDetail.as_view())
]
