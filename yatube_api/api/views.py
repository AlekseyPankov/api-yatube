from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from posts.models import Comment, Group, Post, User
from .serializers import (CommentSerializer, GroupSerializer, PostSerializer,
                          UserSerializer)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.author != self.request.user:
            raise PermissionDenied("Редактировать можно только свой пост.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("Удалять можно только свой пост.")
        instance.delete()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class APIComments(APIView):
    def get(self, request, post_pk):
        post = Post.objects.get(pk=post_pk)
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APICommentsDetail(APIView):
    def get(self, request, post_pk, comment_pk):
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=comment_pk, post=post)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, post_pk, comment_pk):
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=comment_pk, post=post)
        if request.user != comment.author:
            return Response(
                {"detail": "Редактировать комментарий может только автор."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CommentSerializer(instance=comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, post_pk, comment_pk):
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=comment_pk, post=post)
        if request.user != comment.author:
            return Response(
                {"detail": "Редактировать комментарий может только автор."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CommentSerializer(instance=comment, data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_pk, comment_pk):
        post = get_object_or_404(Post, pk=post_pk)
        comment = get_object_or_404(Comment, pk=comment_pk, post=post)
        if request.user != comment.author:
            return Response(
                {"detail": "Удалять комментарий может только автор."},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
