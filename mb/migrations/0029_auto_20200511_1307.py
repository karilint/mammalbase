# Generated by Django 3.0.3 on 2020-05-11 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0028_auto_20200511_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalsourcemeasurementvalue',
            name='unit',
            field=models.CharField(blank=True, help_text='Measurement unit reported.', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='sourcemeasurementvalue',
            name='unit',
            field=models.CharField(blank=True, help_text='Measurement unit reported.', max_length=250, null=True),
        ),
    ]
