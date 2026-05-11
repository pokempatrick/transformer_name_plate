from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import response, status, permissions, viewsets, filters
from django.contrib.auth import authenticate
import numpy as np
import cv2
import tempfile
from django.core.files.uploadedfile import UploadedFile
from read_name_plate.serializers import NamePlateSerializer
from pathlib import Path
import os

from read_name_plate.utils import read_name_plate
# Create your views here.


class ReadNamePlateAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        if request.FILES.get('image'):
            uploaded_image: UploadedFile = request.FILES.get('image')
            allowed_types = ['image/jpeg',
                             'image/png', 'image/jpg', 'image/bpm']
            if uploaded_image.content_type not in allowed_types:
                return response.Response({"message": f"Unsupported file type. Allowed:{allowed_types}"},
                                         status=status.HTTP_400_BAD_REQUEST)
            # Save to temporary file
            temp_file = None

            try:
                with tempfile.NamedTemporaryFile(suffix=Path(uploaded_image.name).suffix, delete=False) as tmp:
                    for chunk in uploaded_image.chunks():
                        tmp.write(chunk)
                    temp_path = tmp.name

                name_plate_informations = read_name_plate(temp_path)
                os.unlink(temp_path)

            except Exception as e:
                # Clean up temp file if it exists
                if temp_file and os.path.exists(temp_path):
                    os.unlink(temp_path)

                return response.Response({"message": f'Processing failed: {str(e)}'},
                                         status=status.HTTP_400_BAD_REQUEST)

            serializer = NamePlateSerializer(data=name_plate_informations)
            if serializer.is_valid():
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return response.Response({"message": "No image sent."}, status=status.HTTP_400_BAD_REQUEST)
