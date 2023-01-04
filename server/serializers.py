from collections import OrderedDict
from rest_framework import serializers

from server import ob_item_types as obit


class SerializerMetaclass(serializers.SerializerMetaclass):
    def __new__(cls, name, bases, attrs):
        if name != 'Serializer':
            match obit.get_schema_type(name):
                case obit.OBType.Element:
                    e = obit.OBElement(name, use_primitive_names=True)
                    for p in e.primitives():
                        attrs[p.name] = serializers.SerializerMethodField()
                        attrs[f'get_{p.name}'] = lambda _, obj: getattr(obj, p.name)
                case _:
                    cls.add_ob_elements(name, attrs)
                    cls.add_ob_objects(name, attrs)
                    cls.add_ob_arrays(name, attrs)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def add_ob_elements(cls, name, attrs):
        elements = attrs.get('ob_elements', None)
        if elements is None:
            elements = obit.elements_of_ob_object(name)
        for e in elements.values():
            attrs[e.name] = serializers.SerializerMethodField()
            attrs[f'get_{e.name}'] = cls._ob_element_serializer(e)

    @classmethod
    def _ob_element_serializer(cls, e: obit.OBElement):
        primitives = e.primitives()
        field_pairs = [(p.name, e.model_field_name(p)) for p in primitives]

        def get_ob_element_field(self, obj):
            return OrderedDict([(p, getattr(obj, f)) for p, f in field_pairs])

        return get_ob_element_field

    @classmethod
    def add_ob_objects(cls, name, attrs):
        objects = attrs.get('ob_objects', None)
        if objects is None:
            objects = obit.objects_of_ob_object(name)
        for o in objects:
            attrs[o] = eval(o, globals(), locals())()

    @classmethod
    def add_ob_arrays(cls, name, attrs):
        arrays = attrs.get('ob_arrays', None)
        if arrays is None:
            arrays = obit.arrays_of_ob_object(name)
        for plural, singular in arrays:
            attrs[plural] = eval(singular, globals(), locals())(many=True, source=f'{singular.lower()}_set')


class Serializer(serializers.Serializer, metaclass=SerializerMetaclass):
    pass


class Location(Serializer):
    pass


class Address(Serializer):
    pass


class AlternativeIdentifier(Serializer):
    pass


class Contact(Serializer):
    pass


class Firmware(Serializer):
    pass


class CertificationAgency(Serializer):
    pass


class Dimension(Serializer):
    pass


class Package(Serializer):
    pass


class ProdCertification(Serializer):
    pass


class ProdInstruction(Serializer):
    pass


class ProdSpecification(Serializer):
    pass


class Warranty(Serializer):
    pass


class Product(Serializer):
    pass
