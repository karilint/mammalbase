"""exports.services - service helpers for export workflows."""

from django.contrib.auth import get_user_model

from .models import ExportFile

User = get_user_model()


def create_export_file_for_user(*, user: User, file=None) -> ExportFile:
    """Create an ExportFile with audit fields set from the given user."""
    return ExportFile.objects.create(
        file=file,
        created_by=user,
        modified_by=user,
    )
