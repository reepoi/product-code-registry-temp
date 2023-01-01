import json
from pathlib import Path
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


class OpenAPIType(enum.Enum):
    BOOLEAN = 'boolean'
    INTEGER = 'integer'
    NUMBER = 'number'
    STRING = 'string'


def field(openapi_type, ob_item_type, **kwargs):
    return dict(
        openapi_type=openapi_type,
        ob_item_type=obit.json_to_item_type(ob_item_type, OB_TAXONOMY),
        **kwargs
    )


def Decimals(name):
    return 'Decimals', models.IntegerField(f'{name} Decimals')


def EndTime(name):
    return 'EndTime', models.CharField(f'{name} EndTime', max_length=TIME_STR_LEN)


def Precision(name):
    return 'Precision', models.IntegerField(f'{name} Precision')


def StartTime(name):
    return 'StartTime', models.CharField(f'{name} StartTime', max_length=TIME_STR_LEN)


def Unit(name, ob_item_type: obit.ItemTypeUnit):
    max_length = max(len(u.id) for u in ob_item_type.units)
    return 'Unit', models.CharField(f'{name} Unit', max_length=max_length)


def Value(name, field_class, ob_item_type=None, **kwargs):
    if field_class is models.CharField:
        if ob_item_type.__class__ is obit.ItemTypeEnum:
            kwargs['max_length'] = max(len(e.id) for e in ob_item_type.enums)
        else:
            kwargs['max_length'] = STR_LEN
    return 'Value', field_class(f'{name} Value', **kwargs)


def TaxonomyElement(name):
    return [EndTime(name), StartTime(name)]


def TaxonomyElementBoolean(name):
    fields = TaxonomyElement(name)
    fields.append(Value(name, models.BooleanField))
    return fields


def TaxonomyElementInteger(name, ob_item_type: obit.ItemType):
    fields = [Value(name, models.IntegerField)]
    if len(ob_item_type.units) > 0:
        fields.append(Unit(name, ob_item_type))
    return fields


def TaxonomyElementNumber(name, ob_item_type: obit.ItemTypeUnit):
    fields = TaxonomyElement(name)
    fields.append(Value(name, models.DecimalField, max_digits=DECIMAL_MAX_DIGITS, decimal_places=DECIMAL_PLACES))
    if len(ob_item_type.units) > 0:
        fields.append(Unit(name, ob_item_type))
    return fields


def TaxonomyElementString(name, ob_item_type):
    fields = TaxonomyElement(name)
    fields.append(Value(name, models.CharField, ob_item_type=ob_item_type))
    return fields


def add_model_fields(attrs):
    ob_elements = attrs['ob_elements']
    for fname, v in ob_elements.items():
        openapi_type, ob_item_type = v['openapi_type'], v['ob_item_type']
        match openapi_type:
            case OpenAPIType.BOOLEAN:
                fields = TaxonomyElementBoolean(fname, ob_item_type)
            case OpenAPIType.INTEGER:
                fields = TaxonomyElementInteger(fname, ob_item_type)
            case OpenAPIType.NUMBER:
                fields = TaxonomyElementNumber(fname, ob_item_type)
            case OpenAPIType.STRING:
                fields = TaxonomyElementString(fname, ob_item_type)
        for f in fields:
            primitive, field = f
            attrs[f'{fname}_{primitive}'] = field


class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        if 'ob_elements' in attrs:
            add_model_fields(attrs)
        return super().__new__(cls, name, bases, attrs, **kwargs)


class Model(models.Model, metaclass=ModelBase):
    pass

    class Meta:
        abstract = True


class Dimensions(Model):
    ob_elements = dict(
        Height=field(OpenAPIType.NUMBER, 'LengthItemType'),
        Length=field(OpenAPIType.NUMBER, 'LengthItemType'),
        Mass=field(OpenAPIType.NUMBER, 'MassItemType'),
        Weight=field(OpenAPIType.NUMBER, 'MassItemType'),
        Width=field(OpenAPIType.NUMBER, 'LengthItemType'),
    )


class Product(Model):
    ob_elements = dict(
        Description=field(OpenAPIType.STRING, 'StringItemType'),
        FileFolderURL=field(OpenAPIType.STRING, 'StringItemType'),
        ProdCode=field(OpenAPIType.STRING, 'StringItemType'),
        ProdDatasheet=field(OpenAPIType.STRING, 'StringItemType'),
        ProdMfr=field(OpenAPIType.STRING, 'StringItemType'),
        ProdName=field(OpenAPIType.STRING, 'StringItemType'),
        ProdType=field(OpenAPIType.STRING, 'ProdTypeItemType'),
    )

    class Meta:
        abstract = False
