from rest_framework.throttling import SimpleRateThrottle


class FailedLoginThrottle(SimpleRateThrottle):
    scope = "failed_login"

    def get_cache_key(self, request, view):
        """Use the client's IP or email as the cache key to track failed attempts."""
        email = request.data.get("email", None)
        password = request.data.get("password", None)
        if not email or not password:
            return None

        return f"failed_login_{email}"
