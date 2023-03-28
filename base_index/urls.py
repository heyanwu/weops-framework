from django.conf.urls import url

from base_index import views

urlpatterns = (
    url(r"^$", views.home),
)