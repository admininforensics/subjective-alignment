from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.licensing.services import LicenceError, SessionError


def api_exception_handler(exc, context):
    if isinstance(exc, LicenceError):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, SessionError):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return exception_handler(exc, context)
