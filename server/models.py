import json
from pathlib import Path
import enum
from django.db import models
import server.ob_item_types as obit


NAME_LEN = 100
STR_LEN = 500
URL_LEN = 1000
TIME_STR_LEN = 100
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


def Unit(name, max_length=STR_LEN):
    return 'Unit', models.CharField(f'{name} Unit', max_length=max_length)


def Value(name, max_length=STR_LEN):
    return 'Value', models.CharField(f'{name} Value', max_length=max_length)


def TaxonomyElement(name):
    return [EndTime(name), StartTime(name)]


def TaxonomyElementBoolean(name):
    fields = TaxonomyElement(name)
    fields.append(Value(name))
    return fields


def TaxonomyElementInteger(name, ob_item_type: obit.ItemTypeUnit):
    fields = [Value(name)]
    if len(ob_item_type.units) > 0:
        max_length = max(len(u.id) for u in ob_item_type.units)
        fields.append(Unit(name, max_length=max_length))
    return TaxonomyElement(name)


def TaxonomyElementNumber(name, ob_item_type: obit.ItemTypeUnit):
    fields = TaxonomyElement(name)
    fields.append(Value(name))
    if len(ob_item_type.units) > 0:
        max_length = max(len(u.id) for u in ob_item_type.units)
        fields.append(Unit(name, max_length=max_length))
    return fields


def TaxonomyElementString(name, ob_item_type: obit.ItemTypeEnum):
    fields = TaxonomyElement(name)
    if ob_item_type.__class__ is obit.ItemType:
        max_length = STR_LEN
    else:
        max_length = max(len(u.id) for u in ob_item_type.enums)
    fields.append(Value(name, max_length=max_length))
    return fields


def add_model_fields(attrs):
    field_metadata = attrs['field_metadata']
    for fname, v in field_metadata.items():
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
        import pdb
        pdb.set_trace()
        add_model_fields(attrs)
        return super().__new__(cls, name, bases, attrs, **kwargs)


class Product(models.Model, metaclass=ModelBase):
    field_metadata = {
        'Description': field(OpenAPIType.STRING, 'StringItemType'),
        'FileFolderURL': field(OpenAPIType.STRING, 'StringItemType'),
        'ProdCode': field(OpenAPIType.STRING, 'StringItemType'),
        'ProdDatasheet': field(OpenAPIType.STRING, 'StringItemType'),
        'ProdMfr': field(OpenAPIType.STRING, 'StringItemType'),
        'ProdName': field(OpenAPIType.STRING, 'StringItemType'),
        'ProdType': field(OpenAPIType.STRING, 'ProdTypeItemType'),
    }

    class Meta:
        abstract = False
