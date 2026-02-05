from rest_framework.throttling import SimpleRateThrottle


class LoginThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        # Throttle by client IP
        ident = self.get_ident(request)
        return f"login:{ident}"


class ForgotPasswordThrottle(SimpleRateThrottle):
    scope = "forgot"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return f"forgot:{ident}"


class ResetPasswordThrottle(SimpleRateThrottle):
    scope = "reset"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return f"reset:{ident}"