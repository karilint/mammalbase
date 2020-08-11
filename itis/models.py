from django.db import models

class TaxonomicUnits(models.Model):
    tsn = models.IntegerField(primary_key=True, unique=True)
    completename = models.CharField(max_length=200)
    hierarchy_string = models.CharField(max_length=200, blank=True, null=True)
    hierarchy = models.CharField(max_length=400, blank=True, null=True)
    common_names = models.CharField(max_length=400, blank=True, null=True)
    tsn_update_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s - %s ' % (self.tsn, self.completename)

    class Meta:
        ordering = ['hierarchy_string']

class SynonymLinks(models.Model):
    tsn = models.ForeignKey(TaxonomicUnits, to_field="tsn", db_column="tsn", related_name='tsn_synonym', null=True, on_delete = models.SET_NULL)
    tsn_accepted = models.ForeignKey(TaxonomicUnits, to_field="tsn", db_column="tsn_accepted", related_name='tsn_accepted', null=True, on_delete = models.SET_NULL)
    tsn_accepted_name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return '%s - %s ' % (self.tsn, self.completename)
