# Generated by Django 2.0 on 2017-12-27 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MRSAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mrsrequest_uuid', models.UUIDField()),
                ('filename', models.CharField(max_length=255)),
                ('creation_datetime', models.DateTimeField(auto_now_add=True, verbose_name="Heure d'enregistrement du fichier")),
                ('binary', models.BinaryField(verbose_name='Attachement')),
            ],
        ),
    ]
