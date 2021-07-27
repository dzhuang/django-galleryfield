import json
import random
import string

import factory
from django.contrib.auth import get_user_model

from demo.models import DemoGallery


def sequenced_image(number, length=5):
    randgen = random.Random()
    name = ("".join(["image_"] + [randgen.choice(string.ascii_letters)
                    for _i in range(length)] + ["%s.jpg" % str(number)]))
    return json.dumps([{
        "url": "/media/images/%s" % name,
        "thumbnailUrl": "/media/cache/a6/ee/%s" % name,
        "name": "%s" % name,
        "size": (number + 1) * 20000,
        "deleteUrl": "javascript:void(0)",
        'pk': number + 1
    }])


class DemoGalleryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DemoGallery

    images = factory.Sequence(sequenced_image)


class UserFactory(factory.django.DjangoModelFactory):
    # https://stackoverflow.com/a/54584075/3437454

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence(lambda n: 'demo-user-%d' % n)
    is_staff = False
    is_superuser = False
    password = 'secret'

    @factory.lazy_attribute
    def email(self):
        return '%s@test.com' % self.username

    class Meta:
        model = get_user_model()

    class Params:
        # declare a trait that adds relevant parameters for admin users
        flag_is_superuser = factory.Trait(
            is_superuser=True,
            is_staff=True,
            username=factory.Sequence(lambda n: 'admin-%d' % n),
        )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", None)
        obj = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        # ensure the raw password gets set after the initial save
        obj.set_password(password)
        obj.save()
        return obj
