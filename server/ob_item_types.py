import enum
import json
import uuid
from pathlib import Path
from typing import Tuple
from dataclasses import dataclass
from django.db import models


NAME_LEN = 100
STR_LEN = 500
URL_LEN = 1000
TIME_STR_LEN = 100
DECIMAL_PLACES = 8
DECIMAL_MAX_DIGITS = DECIMAL_PLACES * 3
OB_TAXONOMY_FILEPATH = Path(__file__).parent / 'references' / 'Master-OB-OpenAPI.json'


def load_ob_taxonomy():
    with open(OB_TAXONOMY_FILEPATH) as f:
        return json.load(f)


OB_TAXONOMY = load_ob_taxonomy()


class TaxonomyElement(enum.Enum):
    Boolean = 'TaxonomyElementBoolean'
    Integer = 'TaxonomyElementInteger'
    Number = 'TaxonomyElementNumber'
    String = 'TaxonomyElementString'


class OBType(enum.Enum):
    Element = enum.auto()
    Object = enum.auto()
    Array = enum.auto()


@dataclass(frozen=True)
class ItemType:
    name: str
    description: str


@dataclass(frozen=True)
class ItemTypeValue:
    id: str
    label: str
    description: str


@dataclass(frozen=True)
class Enum(ItemTypeValue):
    pass


@dataclass(frozen=True)
class Unit(ItemTypeValue):
    pass


@dataclass(frozen=True)
class ItemTypeEnum(ItemType):
    values: Tuple[ItemTypeValue]


@dataclass(frozen=True)
class ItemTypeUnit(ItemType):
    values: Tuple[ItemTypeValue]


@dataclass(frozen=True)
class ItemTypeGroup:
    type: str
    description: str
    group: Tuple[str]


@dataclass
class OBElement:
    name: str
    description: str
    superclass: str
    item_type: ItemType
    item_type_group: ItemTypeGroup

    def __init__(self, name, **Value_opts):
        allOf = OB_TAXONOMY['components']['schemas'][name]
        details = allOf['allOf'][1]

        self.name = name
        self.description = details['description']
        self.superclass = TaxonomyElement(get_schema_superclass(name))
        self.item_type = json_to_item_type(details['x-ob-item-type'])
        self.item_type_group = json_to_item_type_group(details['x-ob-item-type-group'])
        self.Value_opts = Value_opts

    @property
    def grouped_item_type(self):
        if self.item_type_group is None:
            return self.item_type
        kwargs = dict(
            name=self.item_type.name,
            description=self.item_type.description
        )
        if self.item_type_has_enums or self.item_type_has_units:
            kwargs['values'] = tuple(v for v in self.item_type.values if v.id in self.item_type_group.group)
        return self.item_type.__class__(**kwargs)

    @property
    def item_type_has_enums(self):
        return self._item_type_has_values(ItemTypeEnum)

    @property
    def item_type_has_units(self):
        return self._item_type_has_values(ItemTypeUnit)

    def django_model_fields(self):
        match self.superclass:
            case TaxonomyElement.Boolean:
                return self._boolean_fields()
            case TaxonomyElement.Integer:
                return self._integer_fields()
            case TaxonomyElement.Number:
                return self._number_fields()
            case TaxonomyElement.String:
                return self._string_fields()

    def _item_type_has_values(self, item_type_class):
        nonempty_item_type_group = self.item_type_group is None or len(self.item_type_group.group) > 0
        return (
            self.item_type.__class__ is item_type_class
            and len(self.item_type.values) > 0
            and nonempty_item_type_group
        )

    def _field_name(self, primitive_name):
        return f'{self.name}_{primitive_name}'

    def _verbose_field_name(self, primitive_name):
        return f'{self.name} {primitive_name}'

    def _boolean_fields(self):
        return dict(
            EndTime=self._EndTime_field(),
            StartTime=self._StartTime_field(),
            Value=self._Value_field()
        )

    def _integer_fields(self):
        fields = dict(
            EndTime=self._EndTime_field(),
            StartTime=self._StartTime_field(),
            Value=self._Value_field()
        )
        if self.item_type_has_units:
            fields['Unit'] = self._Unit_field()
        return fields

    def _number_fields(self):
        fields = dict(
            Decimals=self._Decimals_field(),
            EndTime=self._EndTime_field(),
            Precision=self._Precision_field(),
            StartTime=self._StartTime_field(),
            Value=self._Value_field()
        )
        if self.item_type_has_units:
            fields['Unit'] = self._Unit_field()
        return fields

    def _string_fields(self):
        return dict(
            EndTime=self._EndTime_field(),
            StartTime=self._StartTime_field(),
            Value=self._Value_field()
        )

    def _Decimals_field(self):
        return models.DecimalField(self._verbose_field_name('Decimals'),
                                   max_digits=DECIMAL_MAX_DIGITS,
                                   decimal_places=DECIMAL_PLACES,
                                   blank=True, null=True)

    def _EndTime_field(self):
        return models.DateTimeField(self._verbose_field_name('EndTime'),
                                    blank=True, null=True)

    def _Precision_field(self):
        return models.IntegerField(blank=True, null=True)

    def _StartTime_field(self):
        return models.DateTimeField(self._verbose_field_name('EndTime'),
                                    blank=True, null=True)

    def _Unit_field(self):
        max_length = max(len(v.id) for v in self.grouped_item_type.values)
        choices = tuple((v.id, v.label) for v in self.grouped_item_type.values)
        return models.CharField(self._verbose_field_name('Unit'),
                                choices=choices,
                                max_length=max_length, blank=True)

    def _Value_field(self):
        match self.superclass:
            case TaxonomyElement.Boolean:
                return models.BooleanField(self._verbose_field_name('Value'),
                                           blank=True, null=True,
                                           **self.Value_opts)
            case TaxonomyElement.Integer:
                return models.IntegerField(self._verbose_field_name('Value'),
                                           blank=True, null=True,
                                           **self.Value_opts)
            case TaxonomyElement.Number:
                return models.DecimalField(self._verbose_field_name('Value'),
                                           max_digits=DECIMAL_MAX_DIGITS,
                                           decimal_places=DECIMAL_PLACES,
                                           blank=True, null=True,
                                           **self.Value_opts)
            case TaxonomyElement.String:
                return self._string_field_by_item_type()

    def _string_field_by_item_type(self):
        match self.item_type.name:
            case 'UUIDItemType':
                field_kwargs = dict(unique=True, editable=False, default=uuid.uuid4)
                copy_values_between_dicts(field_kwargs, self.Value_opts)
                return models.UUIDField(self._verbose_field_name('Value'),
                                        **field_kwargs)
            case _:
                field_kwargs = dict(blank=True, max_length=STR_LEN)
                copy_values_between_dicts(field_kwargs, self.Value_opts)
                if self.item_type_has_enums:
                    field_kwargs['max_length'] = max(len(v.id) for v in self.grouped_item_type.values)
                    field_kwargs['choices'] = tuple((v.id, v.label) for v in self.grouped_item_type.values)
                return models.CharField(self._verbose_field_name('Value'),
                                        **field_kwargs)


def copy_values_between_dicts(dest: dict, source: dict):
    for k, v in source.items():
        dest[k] = v


def json_to_item_type(name: str):
    it = OB_TAXONOMY['x-ob-item-types'][name]
    kwargs = dict(name=name, description=it['description'])
    match it:
        case {'enums': enums}:
            kwargs['values'] = tuple(Enum(id, v['label'], v['description'])
                                     for id, v in enums.items())
            return ItemTypeEnum(**kwargs)
        case {'units': units}:
            kwargs['values'] = tuple(Unit(id, v['label'], v['description'])
                                     for id, v in units.items())
            return ItemTypeUnit(**kwargs)
        case _:
            return ItemType(**kwargs)


def json_to_item_type_group(name: str):
    if name == '':
        return None
    itg = OB_TAXONOMY['x-ob-item-type-groups'][name]
    return ItemTypeGroup(itg['type'], itg['description'], tuple(itg['group']))


def get_ref_schema(ref: str):
    return ref.split('/')[-1]


def get_schema_superclass(name: dict):
    match get_schema_defn(name):
        case {'allOf': [{'$ref': ref}, _]}:
            return get_ref_schema(ref)
        case _:
            raise ValueError(f'"{name}" does not inherit from a superclass.')


def get_schema_defn(name):
    return OB_TAXONOMY['components']['schemas'][name]


def get_schema_type(name):
    match get_schema_defn(name):
        case {'allOf': [{'$ref': ref}, _]}:
            if get_ref_schema(ref) in tuple(t.value for t in TaxonomyElement):
                return OBType.Element
            return OBType.Object
        case {'type': 'object'}:
            return OBType.Object
        case {'type': 'array'}:
            return OBType.Array
        case _:
            raise ValueError(f'Unknown schema definition type: "{name}"')


def ob_object_properties(name):
    match get_schema_defn(name):
        case {'allOf': [{'$ref': _}, {'properties': props}]}:
            return props
        case {'type': 'object', 'properties': props}:
            return props
        case _:
            raise ValueError(f'Unknown OB object schema: "{name}"')


def elements_of_ob_object(name, **Element_Value_opts):
    return {n: OBElement(n, **Element_Value_opts.get(n, {}))
            for n in sorted(ob_object_properties(name))
            if get_schema_type(n) is OBType.Element}


def objects_of_ob_object(name):
    return tuple(n for n in sorted(ob_object_properties(name))
                 if get_schema_type(n) is OBType.Object)


def ob_object_usage_as_array(name, user_schema_names):
    uses = []
    for uname in user_schema_names:
        for array_name in ob_object_properties(uname):
            match get_schema_defn(array_name):
                case {'type': 'array', 'items': {'$ref': ref}}:
                    if name == get_ref_schema(ref):
                        uses.append(uname)
                case _:
                    continue
    return tuple(sorted(uses))
