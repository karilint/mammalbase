# Generated by Django 3.0.3 on 2020-06-09 20:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('itis', '0009_auto_20200609_1733'),
        ('mb', '0040_historicalproximateanalysis_historicalproximateanalysisitem_proximateanalysis_proximateanalysisitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='tsn',
            field=models.ForeignKey(blank=True, db_column='tsn', null=True, on_delete=django.db.models.deletion.SET_NULL, to='itis.TaxonomicUnits'),
        ),
        migrations.AlterField(
            model_name='historicalproximateanalysis',
            name='cited_reference',
            field=models.CharField(blank=True, help_text='Enter the original reference, if not this study.', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='historicalproximateanalysis',
            name='study_time',
            field=models.CharField(blank=True, help_text='Enter the time when this study was performed.', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='historicalproximateanalysisitem',
            name='cited_reference',
            field=models.CharField(blank=True, help_text='Enter the original reference, if not this study.', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='historicalsourcemethod',
            name='name',
            field=models.CharField(help_text='Enter the method described in the Reference', max_length=500),
        ),
        migrations.AlterField(
            model_name='proximateanalysis',
            name='cited_reference',
            field=models.CharField(blank=True, help_text='Enter the original reference, if not this study.', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='proximateanalysis',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mb.SourceLocation'),
        ),
        migrations.AlterField(
            model_name='proximateanalysis',
            name='study_time',
            field=models.CharField(blank=True, help_text='Enter the time when this study was performed.', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='proximateanalysisitem',
            name='cited_reference',
            field=models.CharField(blank=True, help_text='Enter the original reference, if not this study.', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='proximateanalysisitem',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mb.SourceLocation'),
        ),
        migrations.AlterField(
            model_name='sourcemethod',
            name='name',
            field=models.CharField(help_text='Enter the method described in the Reference', max_length=500),
        ),
    ]
