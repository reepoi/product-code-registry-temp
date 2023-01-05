import enum
from django.db import models
from django.contrib import auth
import server.ob_item_types as obit


RELATION_FIELD_KWARGS = dict(on_delete=models.DO_NOTHING, blank=True, null=True)
OB_MODELS = ['ACInput', 'ACOutput', 'Address', 'AlternativeIdentifier',
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
        user_schemas = [m for m in OB_MODELS
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


class ProdName(Model):
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
        WarrantyID=dict(editable=True, blank=True, default='')
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


class User(auth.models.AbstractUser):
    pass


class Edit(models.Model):
    StatusChoice = enum.Enum('Statuses', {s: s[0] for s in ('Approved', 'Pending', 'Rejected')})
    TypeChoice = enum.Enum('Types', {t: t[0] for t in ('Addition', 'Update', 'Deletion')})
    Model = models.CharField(max_length=max(len(m) for m in OB_MODELS))
    InstanceID = models.PositiveBigIntegerField()  # to match BigAutoField
    Field = models.CharField(max_length=obit.max_ob_object_element_name_length(*OB_MODELS))
    Status = models.CharField(choices=[(s.value, s.name) for s in StatusChoice], max_length=max(len(s.value) for s in StatusChoice))
    Type = models.CharField(choices=[(t.value, t.name) for t in TypeChoice], max_length=max(len(t.value) for t in TypeChoice))
    DataSourceComment = models.CharField(max_length=obit.STR_LEN, blank=True)
    DateSubmitted = models.DateTimeField()
    DateApproved = models.DateTimeField(blank=True, null=True)
    DateEffective = models.DateTimeField(blank=True, null=True)
    SubmittedBy = models.ForeignKey(auth.get_user_model(), related_name='edits_submittedby_set', on_delete=models.DO_NOTHING)
    ApprovedBy = models.ForeignKey(auth.get_user_model(), related_name='edits_approvedby_set', on_delete=models.DO_NOTHING, blank=True, null=True)


class EditChar(Edit):
    FieldValue = models.CharField(max_length=obit.STR_LEN, blank=True)
    FieldValueOld = models.CharField(max_length=obit.STR_LEN, blank=True)


class EditDateTime(Edit):
    FieldValue = models.DateTimeField(blank=True, null=True)
    FieldValueOld = models.DateTimeField(blank=True, null=True)


class EditDecimal(Edit):
    FieldValue = models.DecimalField(max_digits=obit.DECIMAL_MAX_DIGITS,
                                     decimal_places=obit.DECIMAL_PLACES,
                                     blank=True, null=True)
    FieldValueOld = models.DecimalField(max_digits=obit.DECIMAL_MAX_DIGITS,
                                        decimal_places=obit.DECIMAL_PLACES,
                                        blank=True, null=True)


class EditPositiveInteger(Edit):
    FieldValue = models.PositiveIntegerField(blank=True, null=True)
    FieldValueOld = models.PositiveIntegerField(blank=True, null=True)


class EditInteger(Edit):
    FieldValue = models.IntegerField(blank=True, null=True)
    FieldValueOld = models.IntegerField(blank=True, null=True)


class EditURL(Edit):
    FieldValue = models.CharField(max_length=obit.URL_LEN, blank=True)
    FieldValueOld = models.CharField(max_length=obit.URL_LEN, blank=True)


class EditUUID(Edit):
    FieldValue = models.UUIDField(blank=True)
    FieldValueOld = models.UUIDField(blank=True)
