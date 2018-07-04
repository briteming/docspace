# django-docspace
django docspace blog
`demo`
> https://www.iloxp.com/

Installation
------------

```bash
pip install django-docspace
```

**Add `docspace` to your `INSTALLED_APPS` setting.**

`urls.py`

```python
urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path(r'blog/', include('docspace.urls')),
]
```

`settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'docspace',
]
```
