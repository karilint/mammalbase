# Generated by Django 3.2.23 on 2024-03-05 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0014_auto_20240305_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='dietset',
            name='data_quality_score',
            field=models.SmallIntegerField(blank=True, default=0, help_text='Data quality score calculated for the data', null=True),
        ),
        migrations.AddField(
            model_name='historicaldietset',
            name='data_quality_score',
            field=models.SmallIntegerField(blank=True, default=0, help_text='Data quality score calculated for the data', null=True),
        ),
        migrations.AlterField(
            model_name='historicalsourcemeasurementvalue',
            name='data_quality_score',
            field=models.SmallIntegerField(blank=True, default=0, help_text='Data quality score calculated for the data', null=True),
        ),
        migrations.AlterField(
            model_name='sourcemeasurementvalue',
            name='data_quality_score',
            field=models.SmallIntegerField(blank=True, default=0, help_text='Data quality score calculated for the data', null=True),
        ),
    ]