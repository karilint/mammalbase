from django.db import migrations, models


def backfill_source_document_citation(apps, schema_editor):
    SourceDocument = apps.get_model('recode_extraction', 'SourceDocument')
    for doc in SourceDocument.objects.all().iterator():
        authors = (doc.authors or 'Unknown').strip()
        title = (doc.title or 'Untitled').strip().rstrip('.')
        citation = f'{authors}, {doc.year}. {title}.' if doc.year else f'{authors}. {title}.'
        SourceDocument.objects.filter(pk=doc.pk).update(citation=citation)


class Migration(migrations.Migration):
    dependencies = [
        ('recode_extraction', '0006_openai_two_pass_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcedocument',
            name='citation',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.RunPython(backfill_source_document_citation, migrations.RunPython.noop),
        migrations.RunSQL(
            sql="""
            ALTER TABLE recode_extraction_extractedassertionmodel
            ADD COLUMN IF NOT EXISTS review_status varchar(20) NOT NULL DEFAULT 'pending',
            ADD COLUMN IF NOT EXISTS edited_value varchar(250) NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS edited_unit varchar(50) NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS reviewer_note longtext NULL,
            ADD COLUMN IF NOT EXISTS reviewed_at datetime(6) NULL,
            ADD COLUMN IF NOT EXISTS reviewed_by_id bigint NULL
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
