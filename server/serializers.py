from collections import OrderedDict

from rest_framework import serializers

from server import models
from server import ob_item_types as obit


class SerializerMetaclass(serializers.SerializerMetaclass):
    def __new__(cls, name, bases, attrs):
        if name != 'Serializer':
            match obit.get_schema_type(name):
                case obit.OBType.Element:
                    e = obit.OBElement(name, use_primitive_names=True)
                    for p in e.primitives():
                        attrs[p.name] = serializers.SerializerMethodField()
                        attrs[f'get_{p.name}'] = lambda _, obj: getattr(obj, p.name)
                case _:
                    cls.add_ob_elements(name, attrs)
                    cls.add_ob_objects(name, attrs)
                    cls.add_ob_arrays(name, attrs)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def add_ob_elements(cls, name, attrs):
        elements = attrs.get('ob_elements', None)
        if elements is None:
            elements = obit.elements_of_ob_object(name)
        for e in elements.values():
            attrs[e.name] = serializers.SerializerMethodField()
            attrs[f'get_{e.name}'] = cls._ob_element_serializer(e)

    @classmethod
    def _ob_element_serializer(cls, e: obit.OBElement):
        primitives = e.primitives()
        field_pairs = [(p.name, e.model_field_name(p)) for p in primitives]

        def get_ob_element(self, o):
            data = OrderedDict()
            for p, f in field_pairs:
                data[p] = getattr(o, f)
                if self.context['unconfirmed_edits']:
                    data[p] = self.context['edits'].get(f, data[p])
            return data
        return get_ob_element

    @classmethod
    def add_ob_objects(cls, name, attrs):
        objects = attrs.get('ob_objects', None)
        if objects is None:
            objects = obit.objects_of_ob_object(name)
        for o in objects:
            attrs[o] = serializers.SerializerMethodField()
            attrs[f'get_{o}'] = cls._ob_object_serializer(o)

    @classmethod
    def _ob_object_serializer(cls, obj_name):
        serializer = eval(obj_name, globals(), locals())

        def get_ob_object(self, o):
            context = self.context.copy()
            context.pop('unconfirmed_edits', None)
            return serializer(getattr(o, obj_name), context=self.context).data

        return get_ob_object

    @classmethod
    def add_ob_arrays(cls, name, attrs):
        arrays = attrs.get('ob_arrays', None)
        if arrays is None:
            arrays = obit.arrays_of_ob_object(name)
        for plural, singular in arrays:
            attrs[plural] = serializers.SerializerMethodField()
            attrs[f'get_{plural}'] = cls._ob_array_serializer(singular)

    @classmethod
    def _ob_array_serializer(cls, array_name_singular):
        serializer = eval(array_name_singular, globals(), locals())
        src = f'{array_name_singular.lower()}_set'

        def get_ob_array(self, o):
            context = self.context.copy()
            context.pop('unconfirmed_edits', None)
            return serializer(getattr(o, src), many=True, context=self.context).data

        return get_ob_array


class Serializer(serializers.Serializer, metaclass=SerializerMetaclass):
    def to_representation(self, o):
        if self.context['unconfirmed_edits']:
            edits = models.Edit.objects.raw(
                """
                SELECT id, server_Edit.FieldName FROM server_Edit JOIN (
                    SELECT FieldName, max(DateSubmitted) as DateSubmitted FROM server_Edit
                    GROUP BY FieldName
                ) as latest_edits
                ON server_Edit.DateSubmitted=latest_edits.DateSubmitted
                AND server_Edit.FieldName=latest_edits.FieldName
                WHERE server_Edit.ModelName=%s
                AND server_Edit.InstanceID=%s
                AND server_Edit.Status=%s
                AND server_Edit.Type=%s;
                """,
                params=(
                    o.__class__.__name__, o.id,
                    models.Edit.StatusChoice.Pending.value,
                    models.Edit.TypeChoice.Update.value
                )
            )
            self.context['edits'] = {e.FieldName: e.FieldValue for e in edits}
        return super().to_representation(o)


class FrequencyAC(Serializer):
    pass


class ACInput(Serializer):
    pass


class PowerACSurge(Serializer):
    pass


class ACOutput(Serializer):
    pass


class Location(Serializer):
    pass


class Address(Serializer):
    pass


class AlternativeIdentifier(Serializer):
    pass


class Contact(Serializer):
    pass


class MPPT(Serializer):
    pass


class DCInput(Serializer):
    pass


class PowerDCPeak(Serializer):
    pass


class DCOutput(Serializer):
    pass


class Firmware(Serializer):
    pass


class CertificationAgency(Serializer):
    pass


class Dimension(Serializer):
    pass


class InverterEfficiencyCECTestResult(Serializer):
    pass


class InverterEfficiency(Serializer):
    pass


class Package(Serializer):
    pass


class ProdCertification(Serializer):
    pass


class ProdInstruction(Serializer):
    pass


class ProdSpecification(Serializer):
    pass


class Warranty(Serializer):
    pass


class ModuleElectRating(Serializer):
    pass


class ProdBattery(Serializer):
    pass


class ProdCell(Serializer):
    pass


class ProdCombiner(Serializer):
    pass


class ProdEnergyStorageSystem(Serializer):
    pass


class ProdGlazing(Serializer):
    pass


class ProdInverter(Serializer):
    pass


class ProdMeter(Serializer):
    pass


class ProdModule(Serializer):
    pass


class ProdName(Serializer):
    pass


class ProdOptimizer(Serializer):
    pass


class ProdWire(Serializer):
    pass


class Product(Serializer):
    def to_representation(self, o):
        kwargs = dict(context=self.context)
        match o:
            case models.Product(prodbattery=p):
                subclass = ProdBattery(p, **kwargs).data
            case models.Product(prodcell=p):
                subclass = ProdCell(p, **kwargs).data
            case models.Product(prodcombiner=p):
                subclass = ProdCombiner(p, **kwargs).data
            case models.Product(prodenergystoragesystem=p):
                subclass = ProdEnergyStorageSystem(p, **kwargs).data
            case models.Product(prodinverter=p):
                subclass = ProdInverter(p, **kwargs).data
            case models.Product(prodmeter=p):
                subclass = ProdMeter(p, **kwargs).data
            case models.Product(prodmodule=p):
                subclass = ProdModule(p, **kwargs).data
            case models.Product(prodoptimizer=p):
                subclass = ProdOptimizer(p, **kwargs).data
            case models.Product(prodwire=p):
                subclass = ProdWire(p, **kwargs).data
            case models.Product():
                subclass = OrderedDict()
        superclass = super().to_representation(o)
        subclass.update(superclass)
        return subclass
