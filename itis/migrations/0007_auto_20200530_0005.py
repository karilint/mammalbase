# Generated by Django 3.0.3 on 2020-05-29 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itis', '0006_synonymlinks_tsn_accepted_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taxonomicunits',
            name='common_names',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='taxonomicunits',
            name='hierarchy',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
