from django.core.exceptions import ValidationError
import re


def validate_file_size(value):
    filesize = value.size

    if filesize > 1048576:
        raise ValidationError("You cannot upload file more than 1Mb")
    else:
        return value


def validate_contact(value):
    if not bool(re.fullmatch(r"\d{9}", str(value))):
        raise ValidationError("Your phone number must have 9 digits exactly.")
    else:
        return value
