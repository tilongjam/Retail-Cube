from django.urls import path
from . import views

app_name = "Dashboard"
urlpatterns = [
    path("", views.index, name="index"),
    path("main_func", views.main_func, name="main_func")
]
