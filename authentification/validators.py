import json
from django.core.exceptions import ValidationError
import re

from helpers.constant import REGION_TYPE


def validate_region(value):
    region_list = []
    for region in REGION_TYPE:
        region_list.append(region[0])
    if set(value).issubset(set(region_list)):
        return value
    else:
        raise ValidationError("You must choose a valid region.")
