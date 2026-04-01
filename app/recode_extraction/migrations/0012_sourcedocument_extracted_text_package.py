from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recode_extraction', '0011_drop_legacy_extractedassertion_snippet_and_unknown_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcedocument',
            name='extracted_text_package',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
