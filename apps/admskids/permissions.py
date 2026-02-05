from rest_framework import permissions


KIDS_ADMIN_ROLE_CODES = {
    "admin",
    "pastor",
    "leader",
    "admskids_admin",
    "admskids_worker",
}


def is_kids_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True
    try:
        return bool(set(user.role_codes) & KIDS_ADMIN_ROLE_CODES)
    except Exception:
        return False


class IsKidsAdminOrReadOnly(permissions.BasePermission):
    """Leitura autenticada; escrita apenas para admin do ADMSKIDS."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return is_kids_admin(request.user)
