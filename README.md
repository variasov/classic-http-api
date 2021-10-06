# Classic HTTP Api

This package provides base for http APIs, based Falcon framework.

Part of project "Classic".

Usage:

```python
from classic.http_api import App


class Reports:
    
    def on_get_for_day(self, request, response):
        response.media = {'day': 'report'}
        
    def on_get_for_month(self, request, response):
        response.media = {'day': 'period'}

        
app = App()

# Will generate URLs:
# /api/reports/for_day
# /api/reports/for_month
app.register(Reports())

# If we need to customize url:
app.register(Reports(), url='/order_reports')
# Urls will be:
# /api/order_reports/for_day
# /api/order_reports/for_month

# We may register methods only:
app.add_method('/reports/daily', Reports(), suffix='for_day')
# Url will be /api/reports/daily

# prefix may be customized in App class:
app = App(prefix='/api/custom')

# Now, URL will be /api/custom/reports/daily
app.add_method('/reports/daily', Reports(), suffix='for_day')

```

Also, App class can transform pydantic.ValidationError, AppError and ErrorsList
from classic.app to formats:

ValidationError:

```json
[
  {
    "type": "namespace.error_code",
    "msg": "Verbose message",
    "loc": ["path", "to", "error"] 
  }
]
```

AppError:

```json
[
  {
    "type": "namespace.error_code",
    "msg": "Verbose message",
    "ctx": {"any_key": "any_useful_info"}
  }
]
```

Also, this response statuses in this cases will be 400.
