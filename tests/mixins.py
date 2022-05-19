from django.test import Client
from tests.factories import UserFactory


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
            self.fail(f"{context_name} does not exist in given response")
        else:
            return value

    def assertResponseHasNoContext(self, response, context_name):  # noqa
        has_context = True
        try:
            response.context[context_name]
        except KeyError:
            has_context = False
        if has_context:
            self.fail(f"{context_name} unexpectedly exist in given response")

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
            print(f"\n-----------context {context_name}-------------")
            print(value)
            print("-----------context end-------------\n")
        except AssertionError:
            print(f"\n-------no value for context {context_name}----------")


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
        return UserFactory(**create_user_kwargs)

    @classmethod
    def create_superuser(cls, create_user_kwargs=None):
        create_user_kwargs = create_user_kwargs or {}
        kwargs = {"flag_is_superuser": True}
        kwargs.update(create_user_kwargs)
        return UserFactory(**kwargs)
