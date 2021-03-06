# Generated by Django 3.0.3 on 2020-05-25 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0036_auto_20200525_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dietset',
            name='gender',
            field=models.ForeignKey(limit_choices_to={'choice_set': 'Gender'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mb.ChoiceValue'),
        ),
        migrations.AlterField(
            model_name='historicaldietset',
            name='gender',
            field=models.ForeignKey(blank=True, db_constraint=False, limit_choices_to={'choice_set': 'Gender'}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mb.ChoiceValue'),
        ),
    ]
