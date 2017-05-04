# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

class APISecret(models.Model):
    '''
    Every user has an associated API Secret Key
    that is created upon user creation.
    This key is used for HMAC authentication when
    accessing the API via a script.

    The user can choose to modify the key by asking for
    re-generation (in case the previous key was compromised)
    '''

    user = models.OneToOneField(User)
    value = models.CharField(max_length=32)
    created_on = models.DateTimeField(auto_now_add=True)

    @classmethod
    def make_secret(self):
        return uuid.uuid4().hex

    def __unicode__(self):
        return '%s, %s' % (self.user, self.value)

def on_user_create(sender, **kw):
    user = kw['instance']
    if not kw['created']:
        return

    s = APISecret.objects.create(
        user=user, value=APISecret.make_secret(),
    )
    s.save()

post_save.connect(on_user_create, sender=User)
