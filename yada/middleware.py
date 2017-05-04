from __future__ import absolute_import

import re
import hmac
import base64
import hashlib

from django.contrib.auth.models import User
from .models import APISecret

class APIMiddleware(object):
    # Adapted from https://github.com/Felspar/django-fost-authn

    def compute_sig(self, request, key, secret):
        # TODO: ensure HTTP_X_AUTH_TIMESTAMP is not too old
        # (to prevent duplicate message attacks)

        msg = [key,
            request.method,
            request.META['HTTP_X_AUTH_TIMESTAMP'],
            str(request.get_full_path())]

        # TODO path above is unicode, forced to str.
        # got to check later

        if request.body:
            msg.append(request.body)

        msg = '\n'.join(msg)

        digest = hmac.new(str(secret), msg, hashlib.sha256).digest()
        sig = base64.standard_b64encode(digest).strip()

        return sig

    def process_request(self, request):

        auth = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth:
            return

        parts = re.findall('HMAC ([^:]*):(.*)', auth)
        if not parts or len(parts[0]) < 2:
            # TODO: log that we got bad auth header
            return

        username, sig_received = parts[0]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # TODO: log that we got a bad username
            return

        if not user.is_active:
            return

        try:
            api_secret = APISecret.objects.get(user=user)
        except APISecret.DoesNotExist:
            # TODO: log that there is no api secret associated
            # with this user!
            return

        sig_computed = self.compute_sig(request, username, api_secret.value)
        if sig_computed != sig_received:
            # TODO: send auth failed api response and log
            return

        request.user = user
