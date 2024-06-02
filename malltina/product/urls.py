from django.urls import re_path
from .views import CheckProductApiView

urlpatterns = [
    re_path(r'^amazon/(?P<product_code>[A-Z0-9]{10})$', CheckProductApiView.as_view(), name='check_product'),
]
