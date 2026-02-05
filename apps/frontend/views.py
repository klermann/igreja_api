from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple, Type

from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import modelform_factory
from django.http import Http404, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import capfirst
from django.views.generic import DeleteView, DetailView, ListView, TemplateView, CreateView, UpdateView


LOCAL_APP_LABELS = {"accounts", "church", "admskids"}


def _get_model_or_404(app_label: str, model_name: str):
    if app_label not in LOCAL_APP_LABELS:
        raise Http404("App não permitido.")
    model = django_apps.get_model(app_label, model_name, require_ready=True)
    if model is None:
        raise Http404("Model não encontrado.")
    return model


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/admin/login/"

    def test_func(self) -> bool:
        user = self.request.user
        return bool(user and user.is_authenticated and user.is_staff)

    def handle_no_permission(self):
        return redirect(f"/admin/login/?next={self.request.path}")


@dataclass
class ModelLink:
    app_label: str
    model_name: str
    verbose_name_plural: str
    url: str


class DashboardView(StaffOnlyMixin, TemplateView):
    template_name = "frontend/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        links: List[ModelLink] = []
        for app_label in sorted(LOCAL_APP_LABELS):
            app_config = django_apps.get_app_config(app_label)
            for model in app_config.get_models():
                model_name = model._meta.model_name
                verbose = capfirst(model._meta.verbose_name_plural)
                url = reverse("frontend:model_list", kwargs={"app_label": app_label, "model_name": model_name})
                links.append(ModelLink(app_label, model_name, verbose, url))
        ctx["model_links"] = links
        return ctx


class BaseModelMixin(StaffOnlyMixin):
    model = None  # filled dynamically

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any):
        self.model = _get_model_or_404(kwargs["app_label"], kwargs["model_name"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model._default_manager.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["app_label"] = self.model._meta.app_label
        ctx["model_name"] = self.model._meta.model_name
        ctx["verbose_name"] = capfirst(self.model._meta.verbose_name)
        ctx["verbose_name_plural"] = capfirst(self.model._meta.verbose_name_plural)
        ctx["list_url"] = reverse("frontend:model_list", kwargs={"app_label": ctx["app_label"], "model_name": ctx["model_name"]})
        ctx["create_url"] = reverse("frontend:model_create", kwargs={"app_label": ctx["app_label"], "model_name": ctx["model_name"]})
        return ctx


class ModelListView(BaseModelMixin, ListView):
    template_name = "frontend/model_list.html"
    paginate_by = 25

    def get(self, request, *args, **kwargs):
        self.q = request.GET.get("q", "").strip()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.q:
            # Simple search across Char/Text fields
            from django.db.models import Q
            q_obj = Q()
            for field in self.model._meta.get_fields():
                if getattr(field, "attname", None) and field.get_internal_type() in {"CharField", "TextField", "EmailField"}:
                    q_obj |= Q(**{f"{field.name}__icontains": self.q})
            if q_obj:
                qs = qs.filter(q_obj)
        return qs.order_by("-pk")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = getattr(self, "q", "")
        # show a small set of columns
        fields = []
        for f in self.model._meta.fields:
            if f.name in {"id"}:
                fields.append(f)
            elif f.get_internal_type() in {"CharField", "EmailField", "IntegerField", "BooleanField", "DateField", "DateTimeField", "ForeignKey"}:
                fields.append(f)
            if len(fields) >= 8:
                break
        ctx["columns"] = fields
        ctx["detail_url_name"] = "frontend:model_detail"
        return ctx


class ModelDetailView(BaseModelMixin, DetailView):
    template_name = "frontend/model_detail.html"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = ctx["object"]
        # field/value pairs
        pairs = []
        for f in self.model._meta.fields:
            name = capfirst(f.verbose_name)
            try:
                val = getattr(obj, f.name)
            except Exception:
                val = "-"
            pairs.append((name, val))
        ctx["pairs"] = pairs
        ctx["edit_url"] = reverse("frontend:model_update", kwargs={"app_label": self.model._meta.app_label, "model_name": self.model._meta.model_name, "pk": obj.pk})
        ctx["delete_url"] = reverse("frontend:model_delete", kwargs={"app_label": self.model._meta.app_label, "model_name": self.model._meta.model_name, "pk": obj.pk})
        return ctx


class ModelFormMixin(BaseModelMixin):
    template_name = "frontend/model_form.html"

    def get_form_class(self):
        # Exclude auto fields and read-only fields
        exclude = []
        for f in self.model._meta.fields:
            if f.auto_created or f.primary_key:
                exclude.append(f.name)
        return modelform_factory(self.model, fields="__all__", exclude=exclude)

    def form_valid(self, form):
        res = super().form_valid(form)
        messages.success(self.request, "Salvo com sucesso.")
        return res

    def get_success_url(self):
        return reverse("frontend:model_detail", kwargs={"app_label": self.model._meta.app_label, "model_name": self.model._meta.model_name, "pk": self.object.pk})


class ModelCreateView(ModelFormMixin, CreateView):
    pass


class ModelUpdateView(ModelFormMixin, UpdateView):
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs["pk"])


class ModelDeleteView(BaseModelMixin, DeleteView):
    template_name = "frontend/model_confirm_delete.html"
    pk_url_kwarg = "pk"

    def get_object(self, queryset=None):
        return self.get_queryset().get(pk=self.kwargs["pk"])

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Excluído com sucesso.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("frontend:model_list", kwargs={"app_label": self.model._meta.app_label, "model_name": self.model._meta.model_name})
