from rest_framework import viewsets, mixins


class ListDestroyViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    pass
