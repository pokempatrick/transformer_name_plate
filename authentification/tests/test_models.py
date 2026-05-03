from rest_framework.test import APITestCase
from authentification.models import User


class TestModel(APITestCase):

    def test_creates_user(self):
        user = User.objects.create_user(
            'cyrce', 'cyretruly@gmail.com', '1234password')
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'cyretruly@gmail.com')
        self.assertFalse(user.is_staff)

    def test_creates_super_user(self):
        user = User.objects.create_superuser(
            'cyrce', 'cyretruly@gmail.com', '1234password')
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'cyretruly@gmail.com')
        self.assertTrue(user.is_staff)

    def test_raises_error_when_no_username_is_supply(self):
        self.assertRaises(
            ValueError, User.objects.create_user, username="",
            email='cyretruly@gmail.com', password='1234password')

    def test_raises_error_with_message_when_no_username_is_supply(self):
        with self.assertRaisesMessage(ValueError, "The given username must be set"):
            User.objects.create_user(
                username='', email='cyretruly@gmail.com', password='1234password')

    def test_raises_error_with_message_when_no_email_is_supply(self):
        with self.assertRaisesMessage(ValueError, "The given email must be set"):
            User.objects.create_user(
                username='patrick', email='', password='1234password')

    def test_creates_superuser_with_is_staff_false(self):
        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True."):
            User.objects.create_superuser(
                username='guy', email='cyretruly@gmail.com', password='1234password', is_staff="False")

    def test_creates_superuser_with_is_superuser_false(self):
        with self.assertRaisesMessage(ValueError, "Superuser must have is_superuser=True."):
            User.objects.create_superuser(
                username='guy', email='cyretruly@gmail.com', password='1234password', is_superuser="False")
