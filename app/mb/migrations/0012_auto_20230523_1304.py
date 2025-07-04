# Generated by Django 3.2.19 on 2023-05-23 10:04

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0011_auto_20230513_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='ash_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='ash_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='cf_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='cf_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='cp_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='cp_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='dm_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='dm_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='ee_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='ee_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='measurement_determined_by',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='measurement_remarks',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='moisture_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='moisture_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='nfe_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='historicalproximateanalysisitem',
            name='nfe_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='ash_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='ash_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='cf_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='cf_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='cp_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='cp_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='dm_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='dm_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='ee_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='ee_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='measurement_determined_by',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='measurement_remarks',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='moisture_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='moisture_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='nfe_dispersion',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=7, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AddField(
            model_name='proximateanalysisitem',
            name='nfe_measurement_method',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
