import json

import factory
from django.contrib.auth import get_user_model

from demo.models import DemoGallery
from galleryfield.models import BuiltInGalleryImage


class UserFactory(factory.django.DjangoModelFactory):
    # https://stackoverflow.com/a/54584075/3437454

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: "demo-user-%d" % n)
    is_staff = False
    is_superuser = False
    password = "secret"

    @factory.lazy_attribute
    def email(self):
        return "%s@test.com" % self.username

    class Meta:
        model = get_user_model()

    class Params:
        # declare a trait that adds relevant parameters for admin users
        flag_is_superuser = factory.Trait(
            is_superuser=True,
            is_staff=True,
            username=factory.Sequence(lambda n: "admin-%d" % n),
        )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", None)
        obj = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        # ensure the raw password gets set after the initial save
        obj.set_password(password)
        obj.save()
        return obj


class BuiltInGalleryImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BuiltInGalleryImage

    image = factory.django.ImageField(color="blue")


class JSONFactory(factory.ListFactory):
    """
    Use with factory.List to make JSON strings.
    """

    @classmethod
    def _generate(cls, create, attrs):
        obj = super()._generate(create, attrs)
        return json.dumps(obj)


class DemoGalleryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DemoGallery

    images = factory.List([], list_factory=JSONFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        creator = kwargs.pop("creator", None)
        images = kwargs.pop("images", None)
        number = kwargs.pop("number_of_images", 1)
        shuffle = kwargs.pop("shuffle", False)
        obj = super()._create(model_class, *args, **kwargs)
        if not images:
            _kwargs = {}
            if creator is not None:
                _kwargs = {"creator": creator}
            _kwargs["size"] = number
            images = BuiltInGalleryImageFactory.create_batch(**_kwargs)
            image_list = [image.pk for image in images]
            shuffle = shuffle and number > 1
        else:
            from collections.abc import Iterable

            assert isinstance(images, Iterable)
            for image in images:
                assert isinstance(image, BuiltInGalleryImage)
            image_list = [image.pk for image in images]
            shuffle = shuffle and len(images) > 1

        if shuffle:
            import random

            random.shuffle(image_list)

        obj.images = image_list
        obj.save()
        return obj
