from django.db import transaction
from django.contrib.auth.models import User

from mb.models import (
    SourceAttribute,
    SourceReference,
    SourceEntity,
    SourceMethod,
    SourceUnit,
    ChoiceValue,
    SourceStatistic,
    SourceChoiceSetOption,
    SourceChoiceSetOptionValue,
    SourceMeasurementValue)
from imports.tools import possible_nan_to_none, possible_nan_to_zero
from .base_importer import BaseImporter


class EtsImporter(BaseImporter):

    @transaction.atomic
    def importRow(self, row):
        headers = list(row.columns.values)

        # if verbatimTraitUnit == 'nan' or verbatimTraitUnit != verbatimTraitUnit or verbatimTraitUnit == 'NA':
        # entityclass = get_entityclass('Taxon', author)
        # attribute = get_sourceattribute(name, reference, entityclass, method, 2, author)
        # if 'verbatimTraitValue' in headers:
        #     vt_value = possible_nan_to_none(getattr(row, 'verbatimTraitValue'))
        # else:
        #     vt_value = None
        # choicesetoption = get_sourcechoicesetoption(vt_value, attribute, author)
        # choicesetoptionvalue = get_sourcechoicesetoptionvalue(taxon, choicesetoption, author)

        # Common assignments
        author = self.get_author(getattr(row, 'author'))
        source_reference = self.get_or_create_source_reference(
            getattr(row, 'references'), author)
        entity_class = self.get_or_create_entity_class(
            getattr(row, 'taxonRank'), author)
        source_entity = self.get_or_create_source_entity(
            getattr(row, 'verbatimScientificName'), source_reference, entity_class, author)
        name = possible_nan_to_none(getattr(row, 'verbatimTraitName'))
        source_method = self.get_or_create_source_method(
            getattr(row, 'measurementMethod'), source_reference, author)
        source_attribute = self.get_or_create_source_attribute(
            name, source_reference, entity_class, source_method, 1, author)
        verbatim_trait_unit = getattr(row, 'verbatimTraitUnit')
        source_unit = self.get_or_create_source_unit(
            verbatim_trait_unit, author)

        column_functions = {
            'verbatimTraitUnit': possible_nan_to_none,
            'verbatimTraitValue': possible_nan_to_zero,
            'sex': self.get_choicevalue_ets(getattr(row, 'sex'), 'Gender', author),
            'measurementRemarks': possible_nan_to_none,
            'associatedReferences': possible_nan_to_none,
            'verbatimEventDate': possible_nan_to_none,
            'verbatimLocality': lambda val: self.get_or_create_source_location(val, source_reference, author),
            'statisticalMethod': self.get_or_create_source_statistic(getattr(row, 'statisticalMethod'), source_reference, author),
            'measurementValue_min': possible_nan_to_zero,
            'measurementValue_max': possible_nan_to_zero,
            'dispersion': possible_nan_to_zero,
            'lifeStage': self.get_choicevalue_ets(getattr(row, 'lifeStage'), 'Lifestage', author),
            'measurementDeterminedBy': possible_nan_to_none,
            'measurementAccuracy': possible_nan_to_none,
            'individualCount': possible_nan_to_zero,
        }

        # Dictionary comprehension for conditional assignments
        row_data = {key: func(getattr(row, key)) for key,
                    func in column_functions.items() if key in headers}

        # Ensure default values for keys not in headers
        default_values = {
            'method': None,
            'remarks': None,
            'vt_value': 0,
            'locality': None,
            'statistic': None,
            'cited_reference': None,
            'mes_min': 0,
            'mes_max': 0,
            'std': 0,
            'lifestage': None,
            'measured_by': None,
            'accuracy': None,
            'count': 0,
            'gender': None,
        }
        count = row_data['individualCount']
        gender = row_data['sex']
        if gender.caption.lower() == 'female':
            n_female = count
        elif gender.caption.lower() == 'male':
            n_male = count
        else:
            n_unknown = count

        model = {
            'source_entity': source_entity,
            'source_attribute': source_attribute,
            'source_location': row_data['verbatimLocality'],
            'n_total': row_data['individualCount'],
            'n_female': n_female,
            'n_male': n_male,
            'n_unknown': n_unknown,
            'minimum': row_data['measurementValue_min'],
            'maximum': row_data['measurementValue_max'],
            'std': row_data['dispersion'],
            'mean': row_data['verbatimTraitValue'],
            'source_statistic': row_data['statisticalMethod'],
            'source_unit': source_unit,
            'gender': row_data['sex'],
            'life_stage': row_data['lifeStage'],
            'measurement_accuracy': row_data['measurementAccuracy'],
            'measured_by': row_data['measurementDeterminedBy'],
            'remarks': row_data['measurementRemarks'],
            'cited_reference': row_data['associatedReferences'],
        }

        row_data = {**default_values, **model}

        # Creating or retrieving DietSet object
        source_measurement,  = SourceMeasurementValue.objects.filter(
            **row_data)

        if source_measurement.exists():
            print("Existing SourceMeasurementMethod found")
            return False
        else:
            source_measurement = SourceMeasurementValue({
                'created_by': author,
                **row_data
            })
            source_measurement.save()
            print("New SourceMeasurementMethod created:",
                  source_measurement)
            return True

    def get_or_create_source_attribute(self, name: str, source_reference: SourceReference, entity_class: SourceEntity, source_method: SourceMethod, type_value: int, author: User):
        """
        Returns a SourceAttribute object if it exists, otherwise creates it.
        """
        source_attribute = SourceAttribute.objects.filter(
            name__iexact=name, reference=source_reference, entity=entity_class, method=source_method, type=type_value
        )

        if source_attribute.exists():
            return source_attribute.first()
        else:
            source_attribute = SourceAttribute(
                name=name, reference=source_reference, entity=entity_class, method=source_method, type=type_value, created_by=author)
            source_attribute.save()
            return source_attribute

    def get_or_create_source_unit(self, trait_unit, author):
        """
        Returns a SourceUnit object if it exists, otherwise creates it.
        """
        if trait_unit == 'nan' or trait_unit != trait_unit or trait_unit == 'NA':
            return None
        else:
            source_unit = SourceUnit.objects.filter(name__iexact=trait_unit)
            if source_unit.exists():
                return source_unit.first()
            else:
                source_unit = SourceUnit(name=trait_unit, created_by=author)
                source_unit.save()
                return source_unit

    def get_choicevalue_ets(self, choice, choice_set, author):
        """
        Returns a ChoiceValue object if it exists, otherwise creates it.
        """
        if choice != choice or choice == 'nan':
            return None
        choiceset_obj = ChoiceValue.objects.filter(
            caption__iexact=choice, choice_set__iexact=choice_set)
        if len(choiceset_obj) > 0:
            return choiceset_obj[0]
        cv = ChoiceValue.objects.create(
            caption=choice, choice_set=choice_set, created_by=author)
        return cv

    def get_or_create_source_statistic(self, statistic: str, source_reference: SourceReference, author: User):
        """
        Returns a SourceStatistic object if it exists, otherwise creates it.
        """
        if statistic != statistic or statistic == 'nan':
            return None
        else:
            source_statistic = SourceStatistic.objects.filter(
                name__iexact=statistic, reference=source_reference)
            if source_statistic.exists():
                return source_statistic.first()
            else:
                source_statistic = SourceStatistic(
                    name=statistic, reference=source_reference, created_by=author)
                source_statistic.save()
                return source_statistic
