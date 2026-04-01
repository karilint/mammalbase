from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recode_extraction', '0005_extractedassertionmodel_edited_unit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourceextractionrun',
            name='pass1_evidence_package',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='sourceextractionrun',
            name='pass2_structured_package',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='sourceextractionrun',
            name='qc_summary',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='extractedassertionmodel',
            name='qc_errors',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='extractedassertionmodel',
            name='unmapped_reason',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
