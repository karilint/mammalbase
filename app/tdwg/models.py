from django.db import models

class Taxon(models.Model):
    scientific_name = models.CharField(max_length=50, help_text="The scientific name of the taxon.")
    taxon_id = models.CharField(max_length=50, null=True, blank=True, help_text="An identifier for the taxon.")
    kingdom = models.CharField(max_length=50, null=True, blank=True, help_text="The kingdom in which the taxon is classified.")
    phylum = models.CharField(max_length=50, null=True, blank=True, help_text="The phylum in which the taxon is classified.")
    # DarwinCore Class
    class_name = models.CharField(max_length=50, null=True, blank=True, help_text="The class in which the taxon is classified.")
    order = models.CharField(max_length=50, null=True, blank=True, help_text="The order in which the taxon is classified.")
    # suborder is not a DarwinCore Class
    suborder = models.CharField(max_length=50, null=True, blank=True, help_text="The suborder in which the taxon is classified.")
    # infraorder is not a DarwinCore Class
    infraorder = models.CharField(max_length=50, null=True, blank=True, help_text="The infraorder in which the taxon is classified.")
    # superfamily is not a DarwinCore Class
    superfamily = models.CharField(max_length=50, null=True, blank=True, help_text="The superfamily in which the taxon is classified.")
    family = models.CharField(max_length=50, null=True, blank=True, help_text="The family in which the taxon is classified.")
    subfamily = models.CharField(max_length=50, null=True, blank=True, help_text="The subfamily in which the taxon is classified.")
    # tribe is not a DarwinCore Class
    tribe = models.CharField(max_length=50, null=True, blank=True, help_text="The tribe in which the taxon is classified.")
    infrageneric_epithet = models.CharField(max_length=50, null=True, blank=True, help_text="The infrageneric part of a binomial name at ranks above species but below genus.")
    genus = models.CharField(max_length=50, null=True, blank=True, help_text="The genus in which the taxon is classified.")
    generic_name = models.CharField(max_length=50, null=True, blank=True, help_text="The genus part of the scientificName without authorship.")
    subgenus = models.CharField(max_length=50, null=True, blank=True, help_text="The subgenus in which the taxon is classified.")
    specific_epithet = models.CharField(max_length=50, null=True, blank=True, help_text="The specific epithet of the taxon.")
    infraspecific_epithet = models.CharField(max_length=50, null=True, blank=True, help_text="The infraspecific epithet of the taxon.")
    cultivar_epithet = models.CharField(max_length=50, null=True, blank=True, help_text="Part of the name of a cultivar, cultivar group or grex that follows the scientific name.")
    taxon_rank = models.CharField(max_length=50, null=True, blank=True, help_text="The taxonomic rank of the taxon.")
    verbatim_taxon_rank = models.CharField(max_length=50, null=True, blank=True, help_text="The taxonomic rank of the taxon as provided.")
    scientific_name_authorship = models.CharField(max_length=150, null=True, blank=True, help_text="The authorship information of the scientific name.")
    vernacular_name = models.CharField(max_length=50, null=True, blank=True, help_text="The vernacular (common) name associated with the taxon.")
    nomenclatural_code = models.CharField(max_length=50, null=True, blank=True, help_text="The nomenclatural code under which the scientificName is constructed.")
    taxonomic_status = models.CharField(max_length=50, null=True, blank=True, help_text="The status of the taxon in the taxonomic hierarchy.")
    taxon_remarks = models.TextField(null=True, blank=True, help_text="Additional information or comments about the taxon.")
    parent_name_usage = models.CharField(max_length=50, null=True, blank=True, help_text="The name (scientificName or higherTaxon) of the parent taxon.")
    accepted_name_usage = models.CharField(max_length=50, null=True, blank=True, help_text="The name (scientificName or higherTaxon) currently accepted as representing the same concept as the name.")
    original_name_usage = models.CharField(max_length=50, null=True, blank=True, help_text="The originally (i.e., historically) applied name.")
    name_published_in = models.CharField(max_length=50, null=True, blank=True, help_text="The literature in which the scientificName was originally established.")
    name_according_to = models.CharField(max_length=50, null=True, blank=True, help_text="A reference to the source in which the taxon name is considered authoritative or correct.")
    nomenclatural_status = models.CharField(max_length=50, null=True, blank=True, help_text="The status related to the original publication of the name and its conformance to the relevant rules of nomenclature. It is based essentially on an algorithm according to the business rules of the code. It requires no taxonomic opinion.")
    name_published_in_year = models.IntegerField(null=True, blank=True, help_text="The year in which the scientificName was published.")
    higher_classification = models.TextField(null=True, blank=True, help_text="A list (concatenated and separated) of taxa names terminating at the rank immediately higher than the taxon referenced in the taxon record.")
    nameAccordingToID = models.CharField(max_length=255, null=True, blank=True, help_text="An identifier for the reference that supports the taxon name in the nameAccordingTo field.")    # Add other fields specific to your use case
    scientific_name_id = models.CharField(max_length=255, null=True, blank=True, help_text="An identifier for the scientific name.")
    accepted_name_usage_id = models.CharField(max_length=255, null=True, blank=True, help_text="An identifier for the accepted name usage.")
    parent_name_usage_id = models.CharField(max_length=255, null=True, blank=True, help_text="An identifier for the parent name usage.")
    name_published_in_id = models.CharField(max_length=255, null=True, blank=True, help_text="An identifier for the publication in which the scientific name was established.")
    taxon_concept_id = models.CharField(max_length=255, null=True, blank=True, help_text="An identifier for the taxon concept.")
    original_name_usage_id = models.CharField(max_length=255, null=True, blank=True, help_text="An identifier for the original name usage.")
    # sort_order is not a DarwinCore Class
    sort_order = models.TextField(null=True, blank=True)
    # display_order is not a DarwinCore Class
    display_order = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.scientific_name
