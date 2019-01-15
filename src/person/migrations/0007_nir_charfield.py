# Generated by Django 2.1.4 on 2019-01-09 17:37

import django.core.validators
from django.db import migrations, models
import person.models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0006_person_confirms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='nir',
            field=models.CharField(max_length=13, validators=[person.models.nir_validate_alphanumeric, django.core.validators.MinLengthValidator(13)], verbose_name='Numéro de sécurité sociale'),
        ),
    ]