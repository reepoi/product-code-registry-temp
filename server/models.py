from django.db import models
import server.ob_item_types as obit


RELATION_FIELD_KWARGS = dict(on_delete=models.DO_NOTHING, blank=True, null=True)
ALL_MODELS = ['ACInput', 'ACOutput', 'Address', 'AlternativeIdentifier',
              'CertificationAgency', 'Contact', 'DCInput', 'DCOutput',
              'Dimension', 'Firmware', 'FrequencyAC', 'InverterEfficiency',
              'InverterEfficiencyCECTestResult', 'Location', 'MPPT',
              'ModuleElectRating', 'Package', 'PowerACSurge', 'PowerDCPeak',
              'ProdBattery', 'ProdCell', 'ProdCertification', 'ProdCombiner',
              'ProdEnergyStorageSystem', 'ProdGlazing', 'ProdInstruction',
              'ProdMeter', 'ProdModule', 'ProdName', 'ProdOptimizer',
              'ProdSpecification', 'ProdWire', 'Product', 'Warranty']


class ModelBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        if name != 'Model':
            match obit.get_schema_type(name):
                case obit.OBType.Element:
                    e = obit.OBElement(name, use_primitive_names=True)
                    for field_name, field in e.model_fields().items():
                        attrs[field_name] = field
                case _:
                    cls.add_ob_elements(name, attrs)
                    cls.add_ob_objects(name, attrs)
            cls.add_ob_array_usages(name, attrs)
        return super().__new__(cls, name, bases, attrs, **kwargs)

    def add_ob_elements(name, attrs):
        elements = attrs.get('ob_elements', None)
        if elements is None:
            elements = obit.elements_of_ob_object(name)
        for e in elements.values():
            for field_name, field in e.model_fields().items():
                attrs[field_name] = field

    def add_ob_objects(name, attrs):
        objects = attrs.get('ob_objects', None)
        if objects is None:
            objects = obit.objects_of_ob_object(name)
        for o in objects:
            attrs[o] = models.OneToOneField(o, **RELATION_FIELD_KWARGS)

    def add_ob_array_usages(name, attrs):
        user_schemas = [m for m in ALL_MODELS
                        if obit.get_schema_type(m) is not obit.OBType.Element]
        arrays = attrs.get('ob_array_usages', None)
        if arrays is None:
            arrays = obit.ob_object_usage_as_array(name, user_schemas)
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


class ProdBattery(Product):
    pass


class ProdCell(Product):
    pass


class ProdCombiner(Product):
    pass


class ProdEnergyStorageSystem(Product):
    pass


class InverterEfficiency(Model):
    pass


class ProdMeter(Product):
    pass


class ProdGlazing(Model):
    pass


class ProdModule(Product):
    pass


class ModuleElectRating(Model):
    pass


class ProdOptimizer(Product):
    pass


class ProdWire(Product):
    pass


class AlternativeIdentifier(Model):
    pass


class MPPT(Model):
    pass


class Warranty(Model):
    ob_elements = obit.elements_of_ob_object(
        'Warranty',
        WarrantyID=dict(editable=True)
    )


class Package(Model):
    pass


class ProdInstruction(Model):
    pass


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


class PowerDCPeak(Model):
    pass


class FrequencyAC(Model):
    pass


class InverterEfficiencyCECTestResult(Model):
    pass


class ACInput(Model):
    pass


class ACOutput(Model):
    pass


class PowerACSurge(Model):
    pass
