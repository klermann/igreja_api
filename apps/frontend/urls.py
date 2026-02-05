from django.urls import path

from . import views

app_name = "frontend"

urlpatterns = [
    path("painel/", views.DashboardView.as_view(), name="dashboard"),

    path("painel/<str:app_label>/<str:model_name>/", views.ModelListView.as_view(), name="model_list"),
    path("painel/<str:app_label>/<str:model_name>/new/", views.ModelCreateView.as_view(), name="model_create"),
    path("painel/<str:app_label>/<str:model_name>/<str:pk>/", views.ModelDetailView.as_view(), name="model_detail"),
    path("painel/<str:app_label>/<str:model_name>/<str:pk>/edit/", views.ModelUpdateView.as_view(), name="model_update"),
    path("painel/<str:app_label>/<str:model_name>/<str:pk>/delete/", views.ModelDeleteView.as_view(), name="model_delete"),
]
