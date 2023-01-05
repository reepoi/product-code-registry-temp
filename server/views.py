from django.shortcuts import render
from rest_framework import viewsets

from server import models
from server import serializers


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.Product

    def get_serializer_context(self):
        super_context = super().get_serializer_context()
        query_params = self.request.query_params
        context = dict(unconfirmed_edits=query_params.get('unconfirmed_edits', '') == 'true')
        context.update(super_context)
        return context


class ProductByProdCodeViewSet(ProductViewSet):
    lookup_field = 'ProdCode_Value'


class ProductByProductIDVeiwSet(ProductViewSet):
    lookup_field = 'ProductID_Value'
    lookup_value_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
