import os
import uuid

from django.conf import settings


def get_user_photo_random_filename(instance, filename):
    """
    Generate a random filename for user photos.

    Args:
        instance: The instance of the model.
        filename: The original filename.

    Returns:
        str: The formatted random filename.
    """
    extension = os.path.splitext(filename)[1]
    return "{}/{}{}".format(settings.USER_PHOTOS, uuid.uuid4(), extension)
