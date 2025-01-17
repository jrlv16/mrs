import datetime
import io
import pytest
import pytz
import os
from uuid import uuid4

from dbdiff.fixture import Fixture
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.backends.base import SessionBase
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test.client import RequestFactory as drf
from django.urls import reverse

from caisse.models import Caisse, Region
from mrsrequest.models import MRSRequest
from mrsrequest.views import MRSRequestCreateView
from mrsuser.models import User


id = mrsrequest_uuid = pytest.fixture(
        lambda: '2b88b740-3920-44e9-b086-c851f58e7ea7')


Fixture.exclude = {
    'mrsrequest.mrsrequest': ['token'],
    'mrsattachment.mrsattachment': ['attachment_file'],
}


@pytest.fixture
def ur(request_factory):
    def user_request(method=None, **kwargs):
        user = None
        if kwargs:
            caisse = None
            kwargs.setdefault('username', str(kwargs))
            kwargs.setdefault('group', 'UPN')
            if 'caisse' in kwargs:
                caisse = kwargs.pop('caisse')
            group = Group.objects.get_or_create(name=kwargs.pop('group'))[0]
            user = User.objects.get_or_create(**kwargs)[0]
            user.groups.add(group)
            if caisse:
                user.caisses.add(caisse)
        return getattr(request_factory(user), method or 'get')('/path')
    return user_request


@pytest.fixture
def dts(days, hours, tz):
    dts = Bunch()
    for day_name, day_args in days.items():
        for hour_name, hour_args in hours.items():
            for tz_name, tz_arg in tz.items():
                var = f'{day_name}_{hour_name}_{tz_name}'
                dts[var] = tz_arg.localize(datetime.datetime(
                    *(day_args + hour_args),
                ))
    return dts


@pytest.fixture
def tz():
    return dict(
        paris=pytz.timezone('Europe/Paris'),
        utc=pytz.utc,
    )


@pytest.fixture
def hours():
    return {'min': (0, 1), 'max': (23, 59)}


@pytest.fixture
def days():
    return dict(
        yesterday=(1999, 12, 31),
        today=(2000, 1, 1),
        tomorrow=(2000, 1, 2),
    )


@pytest.fixture
def su():
    try:
        return User.objects.get(username='su')
    except User.DoesNotExist:
        pass

    user = User.objects.create(username='su')
    user.groups.add(Group.objects.get_or_create(name='Admin')[0])

    return user


class RequestFactory(drf):
    def __init__(self, user=None):
        self.user = user or AnonymousUser()
        super().__init__()

    def generic(self, *args, **kwargs):
        request = super().generic(*args, **kwargs)
        request.session = SessionBase()
        request.user = self.user
        request._messages = default_storage(request)
        return request


@pytest.fixture
def request_factory():
    return RequestFactory


@pytest.fixture
def srf():
    return RequestFactory(AnonymousUser())


@pytest.fixture
def admin():
    return RequestFactory(User.objects.update_or_create(
        username='test',
        defaults=dict(
            profile='superuser',
        ),
    )[0])


@pytest.fixture(scope='class')
def srf_class(request):
    request.cls.srf = RequestFactory(AnonymousUser())


@pytest.fixture
def uuid():
    return str(uuid4())


@pytest.fixture
def upload():
    return InMemoryUploadedFile(
        io.BytesIO(b'aoeu'),
        'field_name',
        'foo.png',
        'image/png',
        4,  # length of b'aoeu'
        None,
    )


class Payload(object):
    def __init__(self, srf):
        self.srf = srf
        self.mrsrequest = MRSRequest(
            id='e29db065-0566-48be-822d-66bd3277d823'
        )
        self.url = reverse('mrsrequest:wizard')
        self.view_class = MRSRequestCreateView
        self.view_kwargs = dict()
        self.session = None
        self.request = None

    def post(self, **data):
        self.request = self.srf.post(self.url, data)
        self.session = self.request.session = (
            self.session or self.request.session
        )
        self.mrsrequest.allow(self.request)
        self.view = self.view_class(request=self.request, **self.view_kwargs)
        self.response = self.view.dispatch(self.request, **self.view_kwargs)


@pytest.fixture
def p(srf):
    return Payload(srf)


@pytest.fixture
def caisse():
    caisse = Caisse.objects.update_or_create(
        pk=9,
        defaults=dict(
            code='010000000',
            number=311,
            name='test',
            active=True,
            liquidation_email='taoeu@aoeu.com',
        )
    )[0]
    region = Region.objects.update_or_create(
        pk=16,
        name="Occitanie",
        cheflieu_code="31555",
        insee_id="76")
    caisse.regions.add(16)
    return caisse


@pytest.fixture
def other_caisse():
    return Caisse.objects.update_or_create(
        pk=10,
        defaults=dict(
            code='110000000',
            number=333,
            name='test inactive',
            active=False,
        )
    )[0]
