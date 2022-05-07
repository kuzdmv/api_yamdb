from rest_framework import viewsets, mixins


class ListDestroyCreateViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    pass
