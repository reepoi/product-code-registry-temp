from django.apps import apps
from django.db import models
import server.ob_item_types as obit


RELATION_FIELD_KWARGS = dict(on_delete=models.DO_NOTHING, blank=True, null=True)


class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        if name != 'Model':
            cls.add_ob_elements(name, attrs)
            cls.add_ob_objects(name, attrs)
            cls.add_ob_array_usages(name, attrs)
        return super().__new__(cls, name, bases, attrs, **kwargs)

    def add_ob_elements(name, attrs):
        elements = attrs.get('ob_elements', None)
        if elements is None:
            elements = obit.elements_of_ob_object(name)
        for e in elements.values():
            for primitive, field in e.django_model_fields().items():
                attrs[f'{e.name}_{primitive}'] = field

    def add_ob_objects(name, attrs):
        objects = attrs.get('ob_objects', None)
        if objects is None:
            objects = obit.objects_of_ob_object(name)
        for o in objects:
            attrs[o] = models.OneToOneField(o, **RELATION_FIELD_KWARGS)

    def add_ob_array_usages(name, attrs):
        NON_FOREIGN_KEY_MODELS = {v.__name__ for v in apps.all_models['server'].values()
                                  if obit.get_schema_type(v.__name__) is not obit.OBType.Element}
        arrays = attrs.get('ob_array_usages', None)
        if arrays is None:
            arrays = obit.ob_object_usage_as_array(name, NON_FOREIGN_KEY_MODELS)
        for a in arrays:
            attrs[a] = models.ForeignKey(a, **RELATION_FIELD_KWARGS)


class Model(models.Model, metaclass=ModelBase):
    pass

    class Meta:
        abstract = True


class Dimension(Model):
    pass


class Product(Model):
    ob_elements = obit.elements_of_ob_object(
        'Product',
        ProdCode=dict(max_length=16)
    )


class CertificationAgency(Model):
    pass


class Location(Model):
    pass


class DCInput(Model):
    pass


class DCOutput(Model):
    pass


class ProdBattery(Model):
    pass


# OB objects used in OB arrays


class AlternativeIdentifier(Model):
    pass


class MPPT(Model):
    pass


class Warranty(Model):
    pass


class Package(Model):
    pass


class ProdInstruction(Model):
    ob_elements = dict(
        ProdInstruction=obit.OBElement('ProdInstruction'),
    )
    ob_objects = tuple()


class ProdSpecification(Model):
    pass


class ProdCertification(Model):
    pass


class Address(Model):
    pass


class Contact(Model):
    pass


class Firmware(Model):
    pass
