# Generated by Django 2.1 on 2018-10-26 11:26

from django.db import migrations


def provision_counter(apps, schema_editor):
    EmailTemplate = apps.get_model('mrsemail', 'emailtemplate')

    reject_templates = EmailTemplate.objects.filter(
        menu='reject'
    )

    for i in reject_templates:
        i.counter = i.mrsrequest_set.count()
        i.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mrsemail', '0004_add_mrsemail_counter'),
    ]

    operations = [
        migrations.RunPython(provision_counter)
    ]