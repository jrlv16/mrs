# Generated by Django 2.0.3 on 2018-04-16 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caisse', '0001_initial'),
        ('mrsuser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='caisses',
            field=models.ManyToManyField(blank=True, null=True, to='caisse.Caisse'),
        ),
    ]