from django.db import transaction
from django.contrib.auth.models import User
import pandas as pd

from mb.models import (
    SourceAttribute,
    SourceReference,
    SourceEntity,
    SourceMethod,
    SourceUnit,
    ChoiceValue,
    SourceStatistic,
    SourceMeasurementValue)
from .base_importer import BaseImporter


class EtsImporter(BaseImporter):

    @transaction.atomic
    def importRow(self, row):
        print("Importing row:", row)
        
        default_values = {
            'verbatimTraitName': None,
            'verbatimTraitUnit': None,
            'verbatimTraitValue': 0,
            'sex': None,
            'measurementRemarks': None,
            'associatedReferences': None,
            'verbatimLocality': None,
            'statisticalMethod': None,
            'measurementValue_min': 0,
            'measurementValue_max': 0,
            'dispersion': 0,
            'lifeStage': None,
            'measurementDeterminedBy': None,
            'measurementAccuracy': None,
            'individualCount': 0,
        }
        
        def get_attr_with_default(row, attr):
            """Get an attribute from row with a default value if it doesn't exist."""
            return getattr(row, attr, default_values.get(attr))

        # if verbatimTraitUnit == 'nan' or verbatimTraitUnit != verbatimTraitUnit or
        # verbatimTraitUnit == 'NA':
        # entityclass = get_entityclass('Taxon', author)
        # attribute = get_sourceattribute(name, reference, entityclass, method, 2, author)
        # if 'verbatimTraitValue' in headers:
        #     vt_value =self.possible_nan_to_none(getattr(row, 'verbatimTraitValue'))
        # else:
        #     vt_value = None
        # choicesetoption = get_sourcechoicesetoption(vt_value, attribute, author)
        # choicesetoptionvalue = get_sourcechoicesetoptionvalue(taxon, choicesetoption, author) 
        # Common assignments
        author = self.get_author(get_attr_with_default(row, 'author'))
        source_reference = self.get_or_create_source_reference(get_attr_with_default(row, 'references'), author)
        entity_class = self.get_or_create_entity_class(get_attr_with_default(row, 'taxonRank'), author)
        source_entity = self.get_or_create_source_entity(get_attr_with_default(row, 'verbatimScientificName'), source_reference, entity_class, author)
        name = self.possible_nan_to_none(get_attr_with_default(row, 'verbatimTraitName'))
        source_method = self.get_or_create_source_method(get_attr_with_default(row, 'measurementMethod'), source_reference, author)
        source_attribute = self.get_or_create_source_attribute(name, source_reference, entity_class, source_method, 1, author)
        verbatim_trait_unit = self.possible_nan_to_none(get_attr_with_default(row, 'verbatimTraitUnit'))
        source_unit = self.get_or_create_source_unit(verbatim_trait_unit, author)
        verbatim_trait_value = self.possible_nan_to_none(get_attr_with_default(row, 'verbatimTraitValue'))
        sex = self.get_choicevalue_ets(self.possible_nan_to_none(get_attr_with_default(row, 'sex')), 'Gender')
        measurement_remarks = self.possible_nan_to_none(get_attr_with_default(row, 'measurementRemarks'))
        associated_references = self.possible_nan_to_none(get_attr_with_default(row, 'associatedReferences'))
        verbatim_locality = self.get_or_create_source_location(get_attr_with_default(row, 'verbatimLocality'), source_reference, author)
        statistical_method = self.get_or_create_source_statistic(get_attr_with_default(row, 'statisticalMethod'), source_reference, author)
        measurement_value_min = self.possible_nan_to_zero(get_attr_with_default(row, 'measurementValue_min'))
        measurement_value_max = self.possible_nan_to_zero(get_attr_with_default(row, 'measurementValue_max'))
        dispersion = self.possible_nan_to_zero(get_attr_with_default(row, 'dispersion'))
        life_stage = self.get_choicevalue_ets(self.possible_nan_to_none(get_attr_with_default(row, 'lifeStage')), 'Lifestage')
        measurement_determined_by = self.possible_nan_to_none(get_attr_with_default(row, 'measurementDeterminedBy'))
        measurement_accuracy = self.possible_nan_to_none(get_attr_with_default(row, 'measurementAccuracy'))
        individual_count = self.possible_nan_to_zero(get_attr_with_default(row, 'individualCount'))
        
        count = individual_count
        n_female = 0
        n_male = 0
        n_unknown = 0
        
        if sex is not None:
            if sex.caption.lower() == 'female':
                n_female = count
            elif sex.caption.lower() == 'male':
                n_male = count
            else:
                n_unknown = count

        model = {
            'source_entity': source_entity,
            'source_attribute': source_attribute,
            'source_location': verbatim_locality,
            'n_total': individual_count,
            'n_female': n_female,
            'n_male': n_male,
            'n_unknown': n_unknown,
            'minimum': measurement_value_min,
            'maximum': measurement_value_max,
            'std': dispersion,
            'mean': verbatim_trait_value,
            'source_statistic': statistical_method,
            'source_unit': source_unit,
            'gender': sex,
            'life_stage': life_stage,
            'measurement_accuracy': measurement_accuracy,
            'measured_by': measurement_determined_by,
            'remarks': measurement_remarks,
            'cited_reference': associated_references,
        }

        # Creating or retrieving DietSet object
        source_measurement  = SourceMeasurementValue.objects.filter(**model)

        if source_measurement.exists():
            print("Existing SourceMeasurementMethod found")
            return False
        else:
            source_measurement = SourceMeasurementValue(created_by=author, **model)
            source_measurement.save()
            print("New SourceMeasurementMethod created:",
                  source_measurement)
            return True

    def get_or_create_source_attribute(self, name: str, source_reference: SourceReference,
                                       entity_class: SourceEntity, source_method: SourceMethod,
                                       type_value: int, author: User):
        """
        Returns a SourceAttribute object if it exists, otherwise creates it.
        """
        
        if name is None:
            return None
        
        source_attribute = SourceAttribute.objects.filter(
            name__iexact=name,
            reference=source_reference,
            entity=entity_class,
            method=source_method,
            type=type_value
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
        if trait_unit == 'nan' or trait_unit is None or trait_unit == 'NA':
            return None
        source_unit = SourceUnit.objects.filter(name__iexact=trait_unit)
        if source_unit.exists():
            return source_unit.first()
        source_unit = SourceUnit(name=trait_unit, created_by=author)
        source_unit.save()
        return source_unit

    def get_choicevalue_ets(self, choice, choice_set):
        """
        Returns a ChoiceValue object if it exists, otherwise creates it.
        """
        if choice is None or choice == 'nan':
            return None
        choiceset_obj = ChoiceValue.objects.filter(
            caption=choice.capitalize(), choice_set=choice_set.capitalize())
        if len(choiceset_obj) > 0:
            return choiceset_obj[0]
        else:
            return None

    def get_or_create_source_statistic(self, statistic: str, source_reference: SourceReference,
                                       author: User):
        """
        Returns a SourceStatistic object if it exists, otherwise creates it.
        """
        if statistic is None or statistic == 'nan':
            return None
        source_statistic = SourceStatistic.objects.filter(
            name__iexact=statistic, reference=source_reference)
        if source_statistic.exists():
            return source_statistic.first()
        source_statistic = SourceStatistic(
            name=statistic, reference=source_reference, created_by=author)
        source_statistic.save()
        return source_statistic
