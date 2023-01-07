from collections import OrderedDict
from pathlib import Path

from django.apps import apps
from django.db import transaction
import flatten_json
import pandas as pd
import numpy as np


DATA_DIR = Path(__file__).parent / 'data'
BATTERY_XLSX = DATA_DIR / 'Battery_List_Data_ADA.xlsx'

BATTERY_TO_OB_FIELD = OrderedDict([
    ('Manufacturer Name', 'ProdBattery.ProdMfr_Value'),
    ('Brand1', None),
    ('Model Number', 'ProdBattery.ProdCode_Value'),
    ('Technology', 'ProdBattery.BatteryChemistryType_Value'),
    ('Description', 'ProdBattery.Description_Value'),
    # Next three are under the super column UL 1973 Certification
    ('Certifying Entity', 'ProdBattery.ProdCertification.0.CertificationAgency.CertificationAgencyName_Value'),
    ('Certification Date', 'ProdBattery.ProdCertification.0.CertificationDate_Value'),
    ('Edition of UL 1973', 'ProdBattery.ProdCertification.0.CertificationTypeProduct_Value'),
    ('Nameplate Energy Capacity', 'ProdBattery.EnergyCapacityNominal_Value'),
    ('Maximum Continuous Discharge Rate2', 'ProdBattery.DCOutput.PowerDCContinuousMax_Value'),
    ('Manufacturer Declared Roundtrip Efficiency', None),
    ('Certified JA12 Control  Strategies1', None),
    ('Declaration for JA12 Submitted1', None),
    ('Notes', None),
    ('CEC Listing Date', None),
    ('Last Update', None)
])


BATTERY_COLOMN_VALUE_TO_OB_VALUE = (
    ('Edition of UL 1973', ('Ed. 2 : 2018', 'UL1973_2_2018')),
    ('Technology', ('Lithium Iron Phosphate', 'LiFePO4')),
    ('Technology', ('Lithium Iron Phospate', 'LiFePO4')),
    ('Technology', ('Lithium Iron\nPhosphate', 'LiFePO4')),
    ('Technology', ('Lithium-Ion', 'LiIon'))
)

MODULE_TO_OB_FIELD = OrderedDict([
    ('Manufacturer', 'ProdModule.Mfr'),
    ('Model Number', 'ProdModule.ProdCode'),
    ('Description', 'ProdModule.Description'),
    ('Safety Certification', 'ProdModule.ProdCertification.CertificationTypeProduct_Value')
])


def upload_cec_battery():
    data = pd.read_excel(BATTERY_XLSX, header=None, names=BATTERY_TO_OB_FIELD.keys())[12:].replace({np.nan: None})
    for col, (old_val, new_val) in BATTERY_COLOMN_VALUE_TO_OB_VALUE:
        convert_val(data, col, old_val, new_val)
    data = [row.to_dict() for _, row in data.iterrows()]
    data = [{ob_path: row[cec_name] for cec_name, ob_path in BATTERY_TO_OB_FIELD.items() if ob_path is not None} for row in data]
    for row in data:
        row['ProdBattery.Dimension.Height_Value'] = None
        row['ProdBattery.DCInput.MPPTNumber_Value'] = None
    data = [flatten_json.unflatten_list(row, '.') for row in data]
    with transaction.atomic():
        for i, d in enumerate(data):
            try:
                save_model_from_dict('', d)
            except Exception as e:
                print(f'FAILED! At data entry {i} with the data:')
                print(d)
                print(f'Original error: {e}')
                assert False, 'Import failed!'


def django_model(model_name):
    return apps.get_model('server', model_name)


def save_model_from_dict(model_name: str, d: dict):
    fk_objs = {}
    kwargs = {}
    for k, v in d.items():
        if isinstance(v, list):
            fk_objs[f'{k.lower()}_set'] = [save_model_from_dict(k, m) for m in v]
        elif isinstance(v, dict):
            submodel = save_model_from_dict(k, v)
            kwargs[k] = submodel
        else:
            kwargs[k] = v
    if model_name != '':
        new_model = django_model(model_name).objects.create(**kwargs)
        if len(fk_objs) > 0:
            for k, v in fk_objs.items():
                getattr(new_model, k).set(v)
                new_model.save()
        return new_model
    return kwargs


def convert_val(df, col, old_val, val):
    df.loc[df[col] == old_val, col] = val
