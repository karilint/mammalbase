# Generated by Django 3.2.19 on 2023-05-23 10:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('imports', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='proximateanalysisitem_ptr',
        ),
        migrations.DeleteModel(
            name='Historicaltest',
        ),
        migrations.DeleteModel(
            name='test',
        ),
    ]