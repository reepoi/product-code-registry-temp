from django.shortcuts import render
from rest_framework import viewsets

from server import models
from server import serializers


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class ProductByProdCodeViewSet(ProductViewSet):
    lookup_field = 'ProdCode_Value'


class ProductByProductIDVeiwSet(ProductViewSet):
    lookup_field = 'ProductID_Value'
    lookup_value_regex = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
