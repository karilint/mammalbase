# Generated by Django 3.0.3 on 2020-09-02 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mb', '0046_auto_20200830_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalmasterreference',
            name='title',
            field=models.CharField(blank=True, help_text='Enter the Title of the Standard Reference', max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='masterreference',
            name='title',
            field=models.CharField(blank=True, help_text='Enter the Title of the Standard Reference', max_length=400, null=True),
        ),
    ]
