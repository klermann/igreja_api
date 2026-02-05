"""Accounts admin registrations.

Keep registrations split across modules. Import modules so their decorators run.
"""

from . import role_admin  # noqa: F401
from . import user_admin  # noqa: F401
