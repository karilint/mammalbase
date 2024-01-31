import re
import numpy
import pandas as pd
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from mb.models import SourceReference
from .tools import possible_nan_to_zero, generate_rank_id



class Check:
    """
    base class for all checks
    """
    def __init__(self, request):
        self.request = request
        self.id = None

    def check_all_ds(self, df, force=False):
        return (
            self.check_headers_ds(df) and 
            self.check_author(df) and 
            self.check_verbatimScientificName(df) and
            self.check_taxonRank(df) and
            self.check_gender(df) and
            self.check_verbatim_associated_taxa(df) and
            self.check_sequence(df) and
            self.check_measurementValue(df) and 
            self.check_part(df) and 
            self.check_references(df, force) and
            self.check_lengths(df)
        )
    
    def check_all_ets(self, df):
        return (
            self.check_headers_ets(df) and
            self.check_author(df) and
            self.check_verbatimScientificName(df) and
            self.check_taxonRank(df) and
            self.check_lengths(df) and
            self.check_min_max(df)
        )
    
    def check_all_pa(self, df, force=False):
        return (
            self.check_headers_pa(df) and
            self.check_author(df) and
            self.check_verbatimScientificName(df, False) and
            self.check_lengths(df) and
            self.check_part(df) and
            self.check_references(df, force) and
            self.check_nfe(df) and
            self.check_cf_valid(df) and
            self.check_measurementValue(df)
        )

    def check_valid_author(self, df):
        counter = 1
        for author in (df.loc[:, 'author']):
            counter += 1
            if author == "nan":
                messages.error(self.request, "The author is empty at row " +  str(counter) + ".")
                return False
            data = SocialAccount.objects.all().filter(uid=author)
            if not data.exists():
                self.id = None
                messages.error(self.request, "The author " + str(author) + " is not a valid ORCID ID at row " +  str(counter) + ".")
                return False
            self.id = data[0].user_id
        return True

    def check_headers_ds(self, df):
        import_headers = list(df.columns.values)
        accepted_headers = ['author', 'verbatimScientificName', 'taxonRank', 'verbatimAssociatedTaxa', 'sequence',  'references']

        for header in accepted_headers:
            if header not in import_headers:
                messages.error(self.request, "The import file does not contain the required headers. The missing header is: " + str(header) + ".")
                return False
        return True
    
    def check_headers_ets(self, df):
        import_headers = list(df.columns.values)
        accepted_headers = ['references', 'verbatimScientificName', 'taxonRank', 'verbatimTraitName', 'verbatimTraitUnit', 'author']

        for header in accepted_headers:
            if header not in import_headers:
                messages.error(self.request, "The import file does not contain the required headers. The missing header is: " + str(header) + ".")
                return False
        return True
    
    def check_headers_pa(self, df):
        import_headers = list(df.columns.values)
        required_headers = [
            'verbatimScientificName',
            'PartOfOrganism',
            'author',
            'references'
            ]
        optional_headers = {
            "individualCount":float,
            "measurementMethod":str,
            "measurementDeterminedBy":str,
            "verbatimLocality":str,
            "measurementRemarks":str,
            "verbatimEventDate":str,
            "verbatimTraitValue__moisture":float,
            "dispersion__moisture":float,
            "measurementMethod__moisture":str,
            "verbatimTraitValue__dry_matter":float,
            "dispersion__dry_matter":float,
            "measurementMethod__dry_matter":str,
            "verbatimTraitValue__ether_extract":float,
            "dispersion__ether_extract":float,
            "measurementMethod__ether_extract":str,
            "verbatimTraitValue__crude_protein":float,
            "dispersion__crude_protein":float,
            "measurementMethod__crude_protein":str,
            "verbatimTraitValue__crude_fibre":float,
            "dispersion__crude_fibre":float,
            "measurementMethod__crude_fibre":str,
            "verbatimTraitValue_ash":float,
            "dispersion__ash":float,
            "measurementMethod_ash":str,
            "verbatimTraitValue__nitrogen_free_extract":float,
            "dispersion__nitrogen_free_extract":float,
            "measurementMethod__nitrogen_free_extract":str,
            "associatedReferences":str
        }
        type_names = {
            int:"a number",
            float:"a number or decimal value",
            str:"text"
        }

        for header in required_headers:
            if header not in import_headers:
                messages.error(self.request, f"The import file does not contain the required headers. The missing header is: {str(header)}.")
                return False
        
        for header in import_headers:
            if header in optional_headers:
                for row, value in enumerate(df.loc[:, header]):
                    if optional_headers[header]!=str:
                        if isinstance(value, str):
                            value = value.replace(",",".")
                        try:
                            df.loc[row, header] = optional_headers[header](value)
                        except ValueError:
                            messages.error(self.request, f"The {header} on row {row+1} is an incorrect type. It should be {type_names[optional_headers[header]]}.")
                            return False
        return True

    def _calculate_nfe(self, row):
        value_sum = sum([possible_nan_to_zero(row[value]) for value in row.keys() if ("verbatimTraitValue" in value and not "nitrogen_free_extract" in value)])
        return min(
            abs(value_sum-100),
            abs(value_sum-1000)
        )

    def check_nfe(self, df):
        missing_nfe_message = "\nNot reported: calculated by difference"
        headers = list(df.columns.values)
        if 'verbatimTraitValue__nitrogen_free_extract' in headers:
            mask = df["verbatimTraitValue__nitrogen_free_extract"].copy()
            mask[mask.notnull()]=""
            new_mm = df['measurementMethod__nitrogen_free_extract'].fillna(mask.fillna(missing_nfe_message))
            new_mm.replace(r'^$', numpy.nan, regex=True, inplace=True)
            df["measurementMethod__nitrogen_free_extract"] = new_mm
            df["verbatimTraitValue__nitrogen_free_extract"].fillna(df.apply(self._calculate_nfe, axis=1), inplace=True)
        else:
            df["measurementMethod__nitrogen_free_extract"] = missing_nfe_message
            df["verbatimTraitValue__nitrogen_free_extract"] = df.apply(self._calculate_nfe, axis=1)
            df["dispersion__nitrogen_free_extract"] = numpy.nan
        
        return True

    def _check_if_plant(self, name):
        rank_id = generate_rank_id(name)
        try:
            kingdom = rank_id[max(rank_id)]['data'][0]['results'][0]['classification_path'].split('-')[0]
        except ValueError: 
            return None
        return kingdom == "Plantae"
    
    def check_cf_valid(self, df):
        headers = list(df.columns.values)
        for row in range(df.shape[0]):
            is_plant = self._check_if_plant(df.loc[row, "verbatimScientificName"])
            if is_plant is None:
                continue
            if is_plant and ('verbatimTraitValue__crude_fibre' not in headers or possible_nan_to_zero(df.loc[row, 'verbatimTraitValue__crude_fibre'])==0):
                messages.error(self.request, f"Item of type plantae is missing required value verbatimTraitValue__crude_fibre on row {row}.")
                return False
        return True

    def check_author(self, df):
        for row, author in enumerate(df.loc[:, 'author'], 1):
            if len(str(author)) != 19:
                messages.error(self.request, f"The author \'{author}\' on row {row} is not in the correct form.")
                return False
            if "X" in author:
                author = author.replace("X", "")
            if "-" in author:
                author = author.replace("-", "")
            if not author.isdigit():
                messages.error(self.request, f"The author \'{author}\' on row {row} is not in the correct form.")
                return False
        return True

    def check_verbatimScientificName(self, df, taxon_rank_included=True):
        for row, name in enumerate(df.loc[:, 'verbatimScientificName'], 1):
            if name == "nan" or pd.isna(name):
                messages.error(self.request, f"Scientific name \'{name}\' is empty at row {row}.")
                return False
            if len(name) > 250:
                messages.error(self.request, f"Scientific name \'{name[:10]}...\' is too long at row {row}.")
                return False
        if not taxon_rank_included:
            return True
        df_new = df[['verbatimScientificName', 'taxonRank']]
        for row, item in enumerate(df_new.values, 1):
            names_list = item[0].split()

            if len(names_list) > 3 and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format on row {row}.")
                return False
            if len(names_list) == 3 and item[1] not in {'Subspecies', 'subspecies'} and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format or taxonomic rank \'{str(item[1])}\' should be 'Subspecies' on row {row}.")
                return False
            if len(names_list) == 2 and item[1] not in {'Species', 'species'} and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format or taxonomic rank \'{str(item[1])}\' should be 'Species' on row {row}.")
                return False
            if len(names_list) == 1 and item[1] not in {'Genus', 'genus'} and not any(x in {"sp.", "sp", "cf.", "cf", "indet.", "indet", "aff.", "aff", "spp.", "spp"} for x in names_list):
                messages.error(self.request, f"Scientific name \'{str(item[0])}\' is not in the correct format or taxonomic rank \'{str(item[1])}\' should be 'Genus' on row {row}.")
                return False
        return True

    def check_taxonRank(self, df):
        counter = 1
        for rank in (df.loc[:, 'taxonRank']):
            counter += 1
            if rank not in ['Genus', 'Species', 'Subspecies', 'genus', 'species', 'subspecies']:
                messages.error(self.request, "Taxonomic rank is not in the correct form on the line " + str(counter) + ".")
                return False
        return True
    
    def check_gender(self, df):
        headers = list(df.columns.values)
        if 'sex' not in headers:
            return True
        counter = 1
        for value in (df.loc[:, 'sex']):
            counter += 1
            if str(value).lower() != 'nan':
                try: 
                    if int(value) != 22 and int(value)!= 23:
                        messages.error(self.request, 'Gender is not in the correct format on the line '+str(counter)+' it should be 22 for male or 23 for female')
                        return False
                except ValueError:
                        messages.error(self.request, 'Gender is not in the correct format on the line '+str(counter)+' it should be 22 for male or 23 for female')
                        return False
        return True


    def check_verbatim_associated_taxa(self, df):
        counter = 1
        for item in (df.loc[:, 'verbatimAssociatedTaxa']):
            counter += 1
            if item == "nan" or pd.isna(item):
                messages.error(self.request, "The line " + str(counter) + " should not be empty on the column 'verbatimAssociatedTaxa'.")
                return False
            if len(item) > 250:
                messages.error(self.request, "verbatimAssociatedTaxa is too long at row " + str(counter) + ".")
                return False
        return True

    def check_sequence(self, df):
        import_headers = list(df.columns.values)
        has_measurementvalue =  "measurementValue" in import_headers
        if has_measurementvalue:
            df_new = df[['verbatimScientificName', 'verbatimAssociatedTaxa', 'sequence', 'references', 'measurementValue']]
        else:
            df_new = df[['verbatimScientificName', 'verbatimAssociatedTaxa', 'sequence', 'references']]
        optional_headers = [
            'verbatimLocality',
            'habitat',
            'samplingEffort',
            'sex',
            'individualCount',
            'verbatimEventDate',
            'measurementMethod',
            'associatedReferences'
        ]
        counter = 0
        total = 1
        fooditems = []
        compare = []

        for lines, item in enumerate(df_new.values,2):
            if str(item[2]).isnumeric():
                if int(item[2]) == counter:
                    if has_measurementvalue:
                        if item[4] > measurementvalue_reference:
                            messages.error(self.request, "Measurement value on the line " + str(lines) + " should not be larger than " + str(measurementvalue_reference) + ".")
                            return False
                    if has_measurementvalue:
                        measurementvalue_reference = item[4]
                    if item[0] != scientific_name:
                        messages.error(self.request, "Scientific name on the line " + str(lines) + " should be '" + str(scientific_name) + "'.")
                        return False
                    if item[3] != references:
                        messages.error(self.request, "References on the line " + str(lines) + " should be '" + str(references) + "'.")
                        return False
                    if item[1] in fooditems:
                        messages.error(self.request, "Food item on the line " + str(lines) + " is already mentioned for this diet set.")
                        return False
                    fooditems.append(item[1])
                    counter += 1
                    total += int(item[2])

                elif int(item[2]) == 1:
                    reference_list = [item[0], item[3]]
                    if has_measurementvalue:
                        measurementvalue_reference = item[4]

                    for header in optional_headers:
                        if header in df.columns.values:
                            reference_list.extend(list(df.loc[lines - 2:lines - 2, header].fillna(0)))

                    if reference_list == compare:
                        messages.error(self.request, "False sequence number 1 on the line " + str(lines) +".")
                        return False

                    total = 1
                    counter = 2
                    scientific_name = item[0]
                    references = item[3]
                    fooditems = [item[1]]
                    compare = reference_list
                    continue

                else:
                    counter_sum = (counter*(counter+1))/2
                    counter -= 1
                    if counter != -1 and counter_sum != total:
                        messages.error(self.request, "Check the sequence numbering on the line " + str(lines) + ".")
                        return False
            else:
                messages.error(self.request, "Sequence number on the line " + str(lines) + " is not numeric.")
                return False
        return True

    def check_measurementValue(self, df):
        import_headers = list(df.columns.values)
        if "measurementValue" in import_headers:
            for row, value in enumerate(df.loc[:, 'measurementValue'], 1):
                if pd.isnull(value) == True or any(c.isalpha() for c in str(value)) == False:
                    pass
                else:
                    messages.error(self.request, f"The measurement value on row {row} is not a number.")
                    return False
                if value <= 0:
                    messages.error(self.request, f"The measurement value on row {row} needs to be bigger than zero.")
                    return False
        elif any('verbatimTraitValue' in header for header in import_headers):
            measurement_headers = [hdr for hdr in import_headers if 'verbatimTraitValue' in hdr or 'dispersion' in hdr]
            for header in measurement_headers:
                for row, value in enumerate(df.loc[:, header], 1):
                    if pd.isnull(value) or not any(c.isalpha() for c in str(value)):
                        pass
                    else:
                        messages.error(self.request, f"The {header} \'{value}\' on row {row} is not a number.")
                        return False
                    if value < 0:
                        messages.error(self.request, f"The {header} \'{value}\' on row {row} should not be negative.")
                        return False
        return True
    
    def check_part(self, df):
        headers = list(df.columns.values)
        accepted = ['BARK', 'BLOOD', 'BONES', 'BUD', 'CARRION', 'EGGS', 'EXUDATES', 'FECES', 'FLOWER', 'FRUIT', 'LARVAE', 'LEAF', 'MINERAL', 'NECTAR/JUICE', 'NONE', 'POLLEN', 'ROOT', 'SEED', 'SHOOT', 'STEM', 'UNKNOWN', 'WHOLE']
        if 'PartOfOrganism' not in headers:
            return True
        for row, value in enumerate(df.loc[:, 'PartOfOrganism'], 1):
            if value.lower() != 'nan' and value.upper() not in accepted:
                messages.error(self.request, f"Part is invalid on row {row}. The accepted part names are: bark, blood, bones, bud, carrion, eggs, exudates, feces, flower, fruit, larvae, leaf, mineral, nectar/juice, none, pollen, root, seed, shoot, stem, unknown, whole")
                return False
        return True

    def check_reference_in_db(self, reference):
        return len(SourceReference.objects.filter(citation__iexact=reference)) == 0

    def check_references(self, df, force:bool):
        for row, ref in enumerate(df.loc[:, 'references'], 1):
            if not force:
                if not self.check_reference_in_db(ref):
                    messages.error(self.request, f"Reference on row {row} already in database. Are you sure you want to import this file? If you are sure use force upload.")
                    return False

            if len(ref) < 10 or len(ref) > 500:
                messages.error(self.request, f"Reference is too short or too long on row {row}.")
                return False
            match = re.match(r'.*([1-2][0-9]{3})', ref)
            if match is None:
                messages.error(self.request, f"Reference does not have a year number on row {row}.")
                return False
        return True
    
    def check_lengths(self, df):
        import_headers = list(df.columns.values)
        all_headers = {
           "verbatimLocality":250,
           "habitat":250,
           "samplingEffort":250,
           "verbatimEventDate":250,
           "measurementMethod":500,
           "associatedReferences":250,
           "verbatimTraitName":250,
           "verbatimTraitValue":250,
           "verbatimTraitUnit":250,
           "measurementDeterminedBy":250,
           "measurementRemarks":250,
           "measurementAccuracy":250,
           "statisticalMethod":250,
           "lifeStage":250,
           "verbatimLatitude":250,
           "verbatimLongitude":250
        }
        for header in all_headers.keys():
            if header in import_headers:
                for row, value in enumerate(df.loc[:, header], 1):
                    if len(str(value)) > all_headers[header]:
                        messages.error(self.request, f"{header} is too long on row {row}.")
                        return False
        return True

    def check_min_max(self, df):
        import_headers = list(df.columns.values)
        
        if "measurementValue_min" in import_headers:
            if "measurementValue_max" not in import_headers:
                messages.error(self.request, "There should be a header called 'measurementValue_max'.")
                return False
        elif "measurementValue_max" in import_headers:
            if "measurementValue_min" not in import_headers:
                messages.error(self.request, "There should be a header called 'measurementValue_min'.")
                return False
        
        if "measurementValue_min" not in import_headers and "measurementValue_max" not in import_headers:
            if "verbatimTraitValue" not in import_headers:
                messages.error(self.request, "There should be header called 'measurementValue_min' and 'measurementValue_max' or a header called 'verbatimTraitValue'.")
                return False
            return True
        
        if "verbatimTraitValue" in import_headers:
            counter = 1
            df_new = df[['measurementValue_min', 'measurementValue_max', 'verbatimTraitValue']]
            for value in df_new.values:
                counter += 1
                if value[0] > value[1]:
                    messages.error(self.request, "Minimum measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                    return False
                if isinstance(value[2], float):
                    if float(value[1]) < float(value[2]):
                        messages.error(self.request, "Mean measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                        return False
                    if float(value[0]) > float(value[2]):
                        messages.error(self.request, "Mean measurement value should be larger than minimum measurement value at row " + str(counter) + ".")
                        return False
                elif value[2][0].isalpha() or value[2][-1].isalpha():
                    if value[1] == 'nan' or pd.isnull(value[1]):
                        continue
                    if value[2] == "nan" or pd.isnull(value[2]):
                        continue
                    messages.error(self.request, "Mean value should be numeric at row " + str(counter) + ".")
                    return False
                elif float(value[1]) < float(value[2]):
                    messages.error(self.request, "Mean measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                    return False
                elif float(value[0]) > float(value[2]):
                    messages.error(self.request, "Mean measurement value should be larger than minimum measurement value at row " + str(counter) + ".")
                    return False
        else:
            counter = 1
            df_new = df[['measurementValue_min', 'measurementValue_max']]
            for value in df_new.values:
                counter += 1
                if value[0] > value[1]:
                    messages.error(self.request, "Minimum measurement value should be smaller than maximum measurement value at row " + str(counter) + ".")
                    return False
        return True
