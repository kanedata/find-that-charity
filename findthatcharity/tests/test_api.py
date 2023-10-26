import django.test

import findthatcharity.apps.ftc.tests
from findthatcharity.api.endpoints import FtcAuthentication


class ApiAuthenticationTest(django.test.TestCase):
    databases = {"data", "admin"}

    def test_authenticate_anon(self):
        request = django.test.RequestFactory().get("/")
        request.user = django.contrib.auth.models.AnonymousUser()

        self.assertEqual(FtcAuthentication().authenticate(request, None), None)

    def test_authenticate_user(self):
        user = django.contrib.auth.models.User.objects.create_user(
            username="testuser",
            email="test@example.com",
        )
        request = django.test.RequestFactory().get("/")
        request.user = user

        self.assertEqual(FtcAuthentication().authenticate(request, None), None)
