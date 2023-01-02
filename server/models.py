from collections import namedtuple
import enum
from django.db import models
import server.ob_item_types as obit


NAME_LEN = 100
STR_LEN = 500
URL_LEN = 1000
TIME_STR_LEN = 100
DECIMAL_PLACES = 8
DECIMAL_MAX_DIGITS = DECIMAL_PLACES * 3
OB_TAXONOMY = obit.load_ob_taxonomy()


class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        if 'ob_elements' in attrs:
            for element in attrs['ob_elements']:
                for primitive, field in element.django_model_fields().items():
                    attrs[f'{element.name}_{primitive}'] = field
        return super().__new__(cls, name, bases, attrs, **kwargs)


class Model(models.Model, metaclass=ModelBase):
    pass

    class Meta:
        abstract = True


class Dimensions(Model):
    ob_elements = (
        obit.OBElement('Height'),
        obit.OBElement('Length'),
        obit.OBElement('Mass'),
        obit.OBElement('Weight'),
        obit.OBElement('Width')
    )


class Product(Model):
    ob_elements = (
        obit.OBElement('Description'),
        obit.OBElement('FileFolderURL'),
        obit.OBElement('ProdCode', max_length=16),
        obit.OBElement('ProdDatasheet'),
        obit.OBElement('ProdMfr'),
        obit.OBElement('ProdName'),
        obit.OBElement('ProdType'),
    )

    class Meta:
        abstract = False
