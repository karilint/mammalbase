# Generated by Django 3.2.18 on 2023-05-12 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tdwg', '0002_auto_20230512_1408'),
        ('mb', '0009_auto_20230214_2051'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalmasterentity',
            name='taxon',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='The associated taxon (optional)', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='tdwg.taxon'),
        ),
        migrations.AddField(
            model_name='masterentity',
            name='taxon',
            field=models.ForeignKey(blank=True, help_text='The associated taxon (optional)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='master_entities', to='tdwg.taxon'),
        ),
    ]
