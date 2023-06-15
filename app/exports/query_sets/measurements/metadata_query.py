#from exports.query_sets.measurements.base_query import query as base_query
from django.db.models.functions import Now, Concat, TruncYear
from django.db.models import Value, Subquery, OuterRef, CharField, Case, When, Exists
from allauth.socialaccount.models import SocialAccount
from datetime import timezone, datetime, timedelta

from exports.query_sets.measurements.base_query import base_query

def metadata_query(measurement_choices):
    base = base_query(measurement_choices)

    now = str(datetime.now(tz=timezone(timedelta(hours=2))).strftime('%Y-%m-%d %H:%M:%S +02:00'))
    now1 = str(datetime.now(tz=timezone(timedelta(hours=2))).strftime('%Y-%m-%dT%H:%M+02:00'))
    now2 = str(datetime.now(tz=timezone(timedelta(hours=2))).strftime('%d %m %Y'))
    year = str(datetime.now(tz=timezone(timedelta(hours=2))).year)


    query = base.annotate(
        dataset_id=Value('https://urn.fi/urn:nbn:fi:att:8dce459f-1401-4c6a-b2bb-c831bd8d3d6f'),
        dataset_name=Value('MammalBase — Dataset 03: Trait Data in Ecological Trait-data Standard (ETS) format'),
        dataset_description=Value(
            'MammalBase - www.mammalbase.net: Trait dataset output in Ecological Trait-data Standard (ETS)'
        ),
        orcid_uid=Subquery(
            SocialAccount.objects.filter(
                user_id=OuterRef('created_by__id')
            ).values_list('uid')[:1]
        ),
        issued=Value(now),
        version=Value(now1),
        bibliographic_citation=Concat(
            Value('The MammalBase community '),
            Value(now),
            Value(' , Data version '),
            Value(now2),
            Value(' at https://mammalbase.org/me/'),
            output_field=CharField()
        ),
        conforms_to=Value(
            ('Ecological Trait-data Standard Vocabulary; v0.10; '
            'URL: https://terminologies.gfbio.org/terms/ets/pages/; '
            'URL: https://doi.org/10.5281/zenodo.1485739')
        ),
        rights_holder=Value(
            'Lintulaakso, Kari;https://orcid.org/0000-0001-9627-8821;Finnish Museum of Natural History LUOMUS'
        ),
        rights=Value('Attribution 4.0 International (CC BY 4.0)'),
        licence=Value('CC BY 4.0')
    ).annotate(
        author=Case(
            When(orcid_uid__startswith='http',
                then='orcid_uid'),
            default=Value('https://orcid.org/0000-0001-9627-8821')
        )
    ).order_by('author').distinct()

    fields = [
        ('dataset_id', 'datasetID'),
        ('dataset_name', 'datasetName'),
        ('dataset_description', 'datasetDescription'),
        ('author', 'author'),
        ('issued', 'issued'),
        ('version', 'version'),
        ('bibliographic_citation', 'bibliographicCitation'),
        ('conforms_to', 'conformsTo'),
        ('rights_holder', 'rightsHolder'),
        ('rights', 'rights'),
        ('licence', 'license'),
    ]

    return query, fields
