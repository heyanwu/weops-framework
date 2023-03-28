from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from blueapps.core.exceptions import ClientBlueException, ServerBlueException


def common_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        import traceback

        print(traceback.format_exc())
        # logger.exception(traceback.format_exc())
        if isinstance(exc, ClientBlueException):
            response = Response(dict(detail=exc.message), status=exc.STATUS_CODE)
        elif isinstance(exc, ServerBlueException):
            response = Response(dict(detail=exc.message), status=exc.STATUS_CODE)
        else:
            response = Response(dict(detail="未知错误"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
