from django.test import SimpleTestCase
from django.urls import reverse, resolve

from read_name_plate import views


class TestUrls(SimpleTestCase):

    def test_read_name_plate_url(self):
        url = reverse('read-name-plate')
        self.assertEqual(resolve(url).func.cls,
                         views.ReadNamePlateAPIView)
