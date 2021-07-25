import json
import random
import string

from django.test import Client
from django.contrib.auth import get_user_model
import factory

from demo.models import DemoGallery


def sequenced_image(number, length=5):
    randgen = random.Random()
    name = ("".join(["image_"] + [randgen.choice(string.ascii_letters)
                    for _i in range(length)] + ["%s.jpg" % str(number)]))
    return json.dumps([{
        "url": "/media/images/%s" % name,
        "thumbnailurl": "/media/cache/a6/ee/%s" % name,
        "name": "%s" % name,
        "size": (number + 1) * 20000,
        "deleteurl": "javascript:void(0)",
        'pk': number + 1
    }])


class DemoGalleryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DemoGallery

    images = factory.Sequence(sequenced_image)


class UserFactory(factory.django.DjangoModelFactory):
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
            username = factory.Sequence(lambda n: 'admin-%d' % n),
        )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", None)
        obj = super(UserFactory, cls)._create(model_class, *args, **kwargs)
        # ensure the raw password gets set after the initial save
        obj.set_password(password)
        obj.save()
        return obj


class ResponseContextMixin(object):
    """
    Response context refers to "the template Context instance that was used
    to render the template that produced the response content".
    Ref: https://docs.djangoproject.com/en/dev/topics/testing/tools/#django.test.Response.context  # noqa
    """
    def get_response_context_value_by_name(self, response, context_name):
        try:
            value = response.context[context_name]
        except KeyError:
            self.fail("%s does not exist in given response" % context_name)
        else:
            return value

    def assertResponseHasNoContext(self, response, context_name):  # noqa
        has_context = True
        try:
            response.context[context_name]
        except KeyError:
            has_context = False
        if has_context:
            self.fail("%s unexpectedly exist in given response" % context_name)

    def assertResponseContextIsNone(self, resp, context_name):  # noqa
        try:
            value = self.get_response_context_value_by_name(resp, context_name)
        except AssertionError:
            # the context item doesn't exist
            pass
        else:
            self.assertIsNone(value)

    def assertResponseContextIsNotNone(self, resp, context_name, msg=""):  # noqa
        value = self.get_response_context_value_by_name(resp, context_name)
        self.assertIsNotNone(value, msg)

    def assertResponseContextEqual(self, resp, context_name, expected_value):  # noqa
        value = self.get_response_context_value_by_name(resp, context_name)
        try:
            self.assertTrue(float(value) - float(expected_value) <= 1e-04)
            return
        except Exception:
            self.assertEqual(value, expected_value)

    def assertResponseContextContains(self, resp,  # noqa
                                      context_name, expected_value, html=False,
                                      in_bulk=False):
        value = self.get_response_context_value_by_name(resp, context_name)
        if in_bulk:
            if not isinstance(expected_value, list):
                expected_value = [expected_value]

            for v in expected_value:
                if not html:
                    self.assertIn(v, value)
                else:
                    self.assertInHTML(v, value)
        else:
            if not html:
                self.assertIn(expected_value, value)
            else:
                self.assertInHTML(expected_value, value)

    def assertResponseContextRegex(  # noqa
            self, resp,  # noqa
            context_name, expected_value_regex):
        value = self.get_response_context_value_by_name(resp, context_name)
        self.assertRegex(value, expected_value_regex)

    def get_response_body(self, response):
        return self.get_response_context_value_by_name(response, "body")

    def debug_print_response_context_value(self, resp, context_name):
        try:
            value = self.get_response_context_value_by_name(resp, context_name)
            print("\n-----------context %s-------------"
                  % context_name)
            print(value)
            print("-----------context end-------------\n")
        except AssertionError:
            print("\n-------no value for context %s----------" % context_name)


class UserCreateMixin(ResponseContextMixin):

    @classmethod
    def setUpTestData(cls):  # noqa
        # Create superuser
        cls.superuser = cls.create_superuser()
        cls.c = Client()
        super().setUpTestData()

    @classmethod
    def create_user(cls, create_user_kwargs=None):
        create_user_kwargs = create_user_kwargs or {}
        return UserFactory.create(**create_user_kwargs)

    @classmethod
    def create_superuser(cls, create_user_kwargs=None):
        create_user_kwargs = create_user_kwargs or {}
        kwargs = {"flag_is_superuser": True}
        kwargs.update(create_user_kwargs)
        return cls.create_user(**kwargs)

