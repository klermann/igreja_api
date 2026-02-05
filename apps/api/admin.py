from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin

# ----------------------------------------------------------------------------
# Third-party admin registrations (make them Unfold-aware)
# ----------------------------------------------------------------------------

# Groups
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


# SimpleJWT token blacklist models (if installed)
try:
    from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken  # type: ignore

    for _m in [OutstandingToken, BlacklistedToken]:
        try:
            admin.site.unregister(_m)
        except admin.sites.NotRegistered:
            pass

    @admin.register(OutstandingToken)
    class OutstandingTokenAdmin(ModelAdmin):
        list_display = ("user", "jti", "created_at", "expires_at")
        search_fields = ("jti", "token")
        list_filter = ("expires_at",)

    @admin.register(BlacklistedToken)
    class BlacklistedTokenAdmin(ModelAdmin):
        list_display = ("token", "blacklisted_at")
        search_fields = ("token__jti",)

except Exception:
    # Token blacklist not installed/enabled
    pass
