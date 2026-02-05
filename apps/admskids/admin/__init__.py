"""ADMSKIDS admin registrations.

This project organizes admin registrations in a dedicated ``admin`` package.
Django admin autodiscover imports ``apps.admskids.admin``; importing the modules
below ensures the @admin.register decorators execute.
"""

from . import attendance_admin  # noqa: F401
from . import enrollment_admin  # noqa: F401
from . import guardian_admin  # noqa: F401
from . import kid_admin  # noqa: F401
from . import kids_class_admin  # noqa: F401
from . import session_admin  # noqa: F401

