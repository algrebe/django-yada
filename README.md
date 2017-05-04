# django-yada
Yet another django API app

## Installation

> Until this is published on pypi, clone and install.

```
virtualenv test-django-yada
source test-django-yada/bin/activate

git clone https://github.com/deep-compute/django-yada.git
cd django-yada
pip install .
```

## Quickstart

Create a project `yadatest` and an app say `polls`

```
django-admin startproject yadatest
cd yadatest
python manage.py startapp polls
```

Add `url(r'^', include('polls.urls')),` to `yadatest/urls.py`
Add `yada` to the `INSTALLED_APPS` list in `yadatest/settings.py`
Add `yada.middleware.APIMiddleware` to the `MIDDLEWARE_CLASSES` list in `yadatest/settings.py`

In `polls/views.py`, create api specs

```python
from django.shortcuts import render

from yada import API, APISpec

# An APISpec is a group of api functions exposed under a particular version

class BaseCalc(APISpec):
    def add(self, request, a, b):
        return a + b

    def subtract(self, request, a, b):
        return a - b

# Over time, we may want to add more functions or alter existing ones.
# Inherit from your previous classes to reuse functionality.

class StandardCalc(BaseCalc):
    def multiply(self, request, a, b):
        return a * b

    def divide(self, request, a, b):
        return a / b

# api will contain the following
# /v1/add /v1/subtract
# /v2/add /v2/subtract (same as v1 since nothing changed)
# /v2/multiply /v2/divide (only available in v2)

api = API(
    BaseCalc(version="v1"),
    StandardCalc(version="v2"),
)
```

Include urls from api in `polls/urls.py` as follows

```python
from django.conf.urls import url, include

from polls.views import api

urlpatterns = [

    # this makes /v1/add -> /api/v1/add
    url(r'^api/', include(api.urls)),
]

```

Create the APISecret model, a superuser, and run the server
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
# fill in the details
python manage.py runserver 8888
```
