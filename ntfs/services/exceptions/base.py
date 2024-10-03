from rest_framework.exceptions import APIException, ValidationError
from .base import *


class PackageValidationError(ValidationError):
    status_code = 400
    default_detail = "Package validation error."
    default_code = "PACKAGE.VALIDATION.ERROR"

    def __init__(self, detail=None, code=None):
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail, code=code)


class InvoiceValidationError(ValidationError):
    status_code = 400
    default_detail = "invoice validation error"
    default_code = "INVOICE.VALIDATION.ERROR"

    def __init__(self, detail=None, code=None):
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail, code=code)


class TPLException(APIException):
    status_code = 500
    default_detail = "A third party logistics error occurred"
    default_code = "TPL.ERROR"

    def __init__(self, detail=None, code=None):
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail=detail, code=code)

# class TPLException(APIException):
#     status_code = 500
#     default_detail = "A third party logistics error occurred"
#     default_code = "TPL.ERROR"

#     def __init__(self, detail=None, code=None):
#         detail = detail if detail is not None else self.default_detail
#         code = f"{self.default_code}.{code}" if code is not None else self.default_code
#         super().__init__(detail=detail, code=code)


class DimensionValidationError(ValidationError):
    status_code = 400
    default_detail = "Dimension validation error."
    default_code = "DIMENSION.VALIDATION.ERROR"

    def __init__(self, detail=None, code=None):
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail, code=code)
