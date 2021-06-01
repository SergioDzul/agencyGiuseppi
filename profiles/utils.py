# -*- coding: utf-8 -*-
__author__ = 'Sergio Dzul'

import hashlib
from logger import log

from django.conf import settings
# from django.template.loader import render_to_string
# from mailer import send_html_mail
from django.utils import timezone


def get_brand():
    brands = dict(settings.BRANDS)
    return brands.get(settings.SITE_ID)


def create_hash(algorithm=None, max_size=None) -> str:
    """
    Create a new unique hash or string value to use as username or token
    by default create a sha1 string with 15 characters long.

    :param function algorithm: algorithm you can pass as hashlib.sha1 or an uuid function.
    :param int max_size: in the case you want truck the string pass the max size.
    :return string: encrypted data
    """
    encrypted_data = ''
    if algorithm is None:
        _hash = hashlib.sha1()
        _hash.update(str(timezone.now()).encode('utf-8'))
        encrypted_data = _hash.hexdigest()
    else:
        try:
            encrypted_data = algorithm(str(timezone.now()).encode('utf-8'))
        except Exception as exception:
            log.error(exception)
    if max_size is not None and isinstance(max_size, int):
        return encrypted_data[:max_size]
    else:
        return encrypted_data
