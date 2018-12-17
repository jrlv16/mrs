# Generated by Django 2.1.3 on 2018-12-10 17:29

from datetime import datetime
import os

from django.conf import settings
from django.db import migrations
from django.db import transaction
from django.db.models import signals

from mrsstat.models import stat_update

FORMAT_EN = '%Y-%m-%d'
FORMAT_FR = '%d/%m/%Y'


def convert_date(date):
    if date is None:
        return date

    try:
        # skip dates already in the right format (like after a downgrade).
        datetime.strptime(date, FORMAT_FR)
    except ValueError:
        pass
    else:
        return date

    return datetime.strptime(date, FORMAT_EN).strftime(FORMAT_FR)


def change_birth_date_format(apps, schema_editor):
    """
    From birth_date yyy-mm-dd to dd/mm/yyyy.
    """
    MRSRequest = apps.get_model('mrsrequest', 'MRSRequest')
    MRSRequestLogEntry = apps.get_model('mrsrequest', 'MRSRequestLogEntry')

    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        return  # this migration only works on pg

    # disable stat auto-recalculate on save
    if not os.getenv('CI'):
        disconnect = signals.post_save.disconnect(stat_update, MRSRequest)
        if not disconnect:
            raise Exception('Could not disable signal')

    requests = MRSRequest.objects.all()
    if len(requests):
        print('--- found: {} requests'.format(len(requests)))

    # request.data = an object with one birth_date
    for request in requests:
        if 'birth_date' not in request.data:
            continue

        new = convert_date(request.data['birth_date'])
        if new == request.data['birth_date']:
            continue

        request.data['birth_date'] = new
        request.save()

    logentries = MRSRequestLogEntry.objects.exclude(
        data__changed__birth_date=None
    )
    print(f'Found {len(logentries)} LogEntries to patch')
    # logentries.data.changed = dict with a list of birth_date
    for entry in logentries:
        if entry.data and 'birth_date' in entry.data.get('changed', {}):
            dates = entry.data['changed']['birth_date']
            for i, date in enumerate(dates):
                new = convert_date(date)
                if new == date:
                    continue

                dates[i] = new

        entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mrsrequest', '0028_initial_data_distancevp'),
    ]

    operations = [
        migrations.RunPython(
            change_birth_date_format,
            lambda apps, schema_editor: True  # allow migration reveres
        ),
    ]
