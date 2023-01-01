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


def Decimals_field():
    return models.IntegerField()


def EndTime_field():
    return models.CharField(max_length=TIME_STR_LEN)


def Precision_field():
    return models.IntegerField()


def StartTime_field():
    return models.CharField(max_length=TIME_STR_LEN)


def Unit_field(max_length=STR_LEN):
    return models.CharField(max_length=max_length)


def Value_field(max_length=STR_LEN):
    return models.CharField(max_length=max_length)


def add_model_fields(m):
    for fname, v in m.field_metadata.items():
        openapi_type, ob_item_type = v['openapi_type'], v['ob_item_type']
        for p, f in zip(['Decimals', 'EndTime', 'Precision', 'StartTime', 'Unit', 'Value'], [Decimals_field, EndTime_field, Precision_field, StartTime_field, Unit_field, Value_field]):
            setattr(m, f'{fname}_{p}', f())


class Product(models.Model):
    field_metadata = {
        'Description': field(OpenAPIType.STRING, 'StringItemType', max_length=STR_LEN),
        'FileFolderURL': field(OpenAPIType.STRING, 'StringItemType', max_length=URL_LEN),
    }

    class Meta:
        abstract = True


all_models = [Product]
for m in all_models:
    add_model_fields(m)
