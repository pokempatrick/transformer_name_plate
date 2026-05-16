import io
from PIL import Image
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from authentification.models import User


class ReadNamePlateTests(APITestCase):
    def setUp(self):
        # Update 'read-name-plate' with the actual name defined in your urls.py
        self.url = reverse('read-name-plate')
        self.user_technicien = User.objects.create(
            username='cyrce_technicien',
            email='cyretruly_technicien@gmail.com',
            first_name="john",
            last_name="does",
            password='1234password',
            role_name="ROLE_TECHNICIEN",
            first_contact=333333453,
        )
        self.user_anonyme = User.objects.create(
            username='cyrce_anonyme',
            email='cyretrul_anonymey@gmail.com',
            first_name="john",
            last_name="does",
            password='1234password',
            role_name="ROLE_ANONYME",
            first_contact=333333453,
        )

    def generate_mock_image(self):
        """Helper to create a simple image file in memory."""
        file = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
        image.save(file, 'png')
        file.name = 'test_image.png'
        file.seek(0)
        return SimpleUploadedFile(file.name, file.read(), content_type='image/png')

    @patch('read_name_plate.views.read_name_plate')
    def test_read_name_plate_success(self, mock_read_func):
        # Mock the return value that the serializer expects
        mock_data = {
            "vendor": "Example Plate",
            "serial_number": "12345",
            "nominal_tension": 15000,
            "power": 160,
        }
        mock_read_func.return_value = mock_data

        image = self.generate_mock_image()
        response = self.client.post(
            self.url, {'image': image}, **{'HTTP_AUTHORIZATION': f'Bearer {self.user_technicien.token}'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the returned data matches what we mocked
        # self.assertEqual(response.data, mock_data)
        mock_read_func.assert_called_once()

    def test_read_name_plate_no_image(self):
        """Test the behavior when no image is provided."""
        response = self.client.post(self.url, {
        }, **{'HTTP_AUTHORIZATION': f'Bearer {self.user_technicien.token}'}, format='multipart')

        # Based on current view logic, it returns None/Empty if no image provided
        # You might want to update the view to return 400 Bad Request instead
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_name_plate_with_bad_role(self):
        """ Test behavoir when the the use has a role anonyme """
        image = self.generate_mock_image()
        response = self.client.post(
            self.url, {'image': image}, **{'HTTP_AUTHORIZATION': f'Bearer {self.user_anonyme.token}'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
