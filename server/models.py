from django.db import models
import server.ob_item_types as obit


RELATION_FIELD_KWARGS = dict(on_delete=models.DO_NOTHING, blank=True, null=True)


class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        if name != 'Model':
            cls.add_ob_elements(name, attrs)
            # cls.add_ob_objects(name, attrs)
        return super().__new__(cls, name, bases, attrs, **kwargs)

    def add_ob_elements(name, attrs):
        elements = attrs.get('ob_elements', None)
        if elements is None:
            elements = obit.elements_of_ob_object(name)
        for e in elements.values():
            for primitive, field in e.django_model_fields().items():
                attrs[f'{e.name}_{primitive}'] = field
        if 'test_class' in attrs:
            attrs['ACInput'] = models.ForeignKey(attrs['test_class'][0], **RELATION_FIELD_KWARGS)

    def add_ob_objects(name, attrs):
        objects = attrs.get('ob_objects', None)
        if objects is None:
            objects = obit.objects_of_ob_object(name)
        if objects is not None:
            for o in objects:
                name = o.__name__
                attrs[name] = models.OneToOneField(o, **RELATION_FIELD_KWARGS)


class Model(models.Model, metaclass=ModelBase):
    pass

    class Meta:
        abstract = True


class ACInput(Model):
    pass


class Dimension(Model):
    test_class = [ACInput]
    pass


class Product(Model):
    ob_elements = obit.elements_of_ob_object(
        'Product',
        ProdCode=dict(max_length=16)
    )
    ob_objects = (Dimension,)
    # Dimension = models.OneToOneField(Dimension, **RELATION_FIELD_KWARGS)


class Package(Model):
    Dimension = models.ForeignKey(Dimension, **RELATION_FIELD_KWARGS)
    Product = models.ForeignKey(Product, **RELATION_FIELD_KWARGS)


class ProdInstruction(Model):
    ob_elements = dict(
        ProdInstruction=obit.OBElement('ProdInstruction'),
    )
    Product = models.ForeignKey(Product, **RELATION_FIELD_KWARGS)


class ProdSpecification(Model):
    Product = models.ForeignKey(Product, **RELATION_FIELD_KWARGS)


class CertificationAgency(Model):
    pass


class ProdCertification(Model):
    CertificationAgency = models.OneToOneField(CertificationAgency, **RELATION_FIELD_KWARGS)
    Product = models.ForeignKey(Product, **RELATION_FIELD_KWARGS)


class Location(Model):
    pass


class Address(Model):
    Location = models.OneToOneField(Location,  **RELATION_FIELD_KWARGS)
    CertificationAgency = models.ForeignKey(CertificationAgency, **RELATION_FIELD_KWARGS)


class Contact(Model):
    Address = models.OneToOneField(Address, **RELATION_FIELD_KWARGS)
    CertificationAgency = models.ForeignKey(CertificationAgency, **RELATION_FIELD_KWARGS)


class Firmware(Model):
    ProdCertification = models.ForeignKey(ProdCertification, **RELATION_FIELD_KWARGS)


class Warranty(Model):
    Product = models.ForeignKey(Product, **RELATION_FIELD_KWARGS)


class AlternativeIdentifier(Model):
    Product = models.ForeignKey(Product, **RELATION_FIELD_KWARGS)


class DCInput(Model):
    pass


class MPPT(Model):
    DCInput = models.ForeignKey(DCInput, **RELATION_FIELD_KWARGS)


class ProdBattery(Model):
    DCInput = models.OneToOneField(DCInput, **RELATION_FIELD_KWARGS)
