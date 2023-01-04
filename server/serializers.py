from collections import OrderedDict
from rest_framework import serializers


from server import ob_item_types as obit


class SerializerMetaclass(serializers.SerializerMetaclass):
    def __new__(cls, name, bases, attrs):
        if name != 'Serializer':
            cls.add_ob_elements(name, attrs)
            cls.add_ob_objects(name, attrs)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def add_ob_elements(cls, name, attrs):
        elements = obit.elements_of_ob_object(name)
        for e in elements.values():
            attrs[e.name] = serializers.SerializerMethodField()
            attrs[f'get_{e.name}'] = cls._ob_element_serializer(e)

    @classmethod
    def _ob_element_serializer(cls, oe: obit.OBElement):
        primitives = oe.primitives()
        field_pairs = [(p.name, oe.model_field_name(p)) for p in primitives]

        def get_ob_element_field(self, obj):
            return OrderedDict([(p, getattr(obj, f)) for p, f in field_pairs])

        return get_ob_element_field

    @classmethod
    def add_ob_objects(cls, name, attrs):
        objects = obit.objects_of_ob_object(name)
        for o in objects:
            attrs[o] = eval(o, globals(), locals())()


class Serializer(serializers.Serializer, metaclass=SerializerMetaclass):
    pass


class Dimension(Serializer):
    pass


class Product(Serializer):
    pass
