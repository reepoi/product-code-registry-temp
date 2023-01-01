import json
from pathlib import Path
from typing import Tuple
from dataclasses import dataclass


OB_TAXONOMY_FILEPATH = Path(__file__).parent / 'references' / 'Master-OB-OpenAPI.json'


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
    enums: Tuple[ItemTypeValue]


@dataclass(frozen=True)
class ItemTypeUnit(ItemType):
    units: Tuple[ItemTypeValue]


def load_ob_taxonomy():
    with open(OB_TAXONOMY_FILEPATH) as f:
        return json.load(f)


def json_to_item_type(name: str, ob_taxonomy: dict):
    it = ob_taxonomy['x-ob-item-types'][name]
    get_item_type_values = lambda key, val_class: tuple(val_class(id, v['label'], v['description'])
                                                        for id, v in it[key].items())
    if 'enums' in it:
        return ItemTypeEnum(name, it['description'], get_item_type_values('enums', Enum))
    elif 'units' in it:
        return ItemTypeUnit(name, it['description'], get_item_type_values('units', Unit))
    else:
        return ItemType(name, it['description'])
