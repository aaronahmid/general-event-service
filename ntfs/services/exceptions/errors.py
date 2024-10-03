from rest_framework.exceptions import APIException, ValidationError  # type: ignore


class CustomAPIError(APIException):
    status_code = 500
    default_detail = "An unexpected error occurred."
    default_code = "error"


class ServiceUnavailable(APIException):
    status_code = 500
    default_detail = "service is down unavailable"
    default_code = "SERVICE.UNAVAILABLE"

    def __init__(self, detail=None, code=None):
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail=detail, code=code)


class ObjectAlreadyExistError(APIException):
    status_code = 409
    default_detail = "Object already exists"
    default_code = "OBJECT.ALREADY.EXISTS"

    def __init__(self, detail=None, code=None):
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail=detail, code=code)


class SenderEmailValidationError(ValidationError):
    def __init__(self, detail=None, code=None):
        default = "ORDER.SENDER.CONTACT.EMAIL"
        code = (
            f"{default}.{code}"
            if code is not None
            else "ORDER.SENDER.CONTACT.EMAIL.REQUIRED"
        )
        super().__init__(detail, code=code)


class UnprocessableContent(APIException):
    status_code = 422
    default_detail = "could not process content"
    default_code = "UNPROCESSABLE.CONTENT"

    def __init__(self, detail=None, code=None):
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail=detail, code=code)


class APIClientException(APIException):
    default_detail = "an exception occurred while trying the request"
    default_code = "CLIENT.ERROR"

    def __init__(self, detail=None, code=None, status_code=None):
        print(detail, status_code, "In here")
        print("in handler!!!!!!!!!!!")
        self.status_code = status_code if status_code is not None else self.status_code
        detail = detail if detail is not None else self.default_detail
        code = f"{self.default_code}.{code}" if code is not None else self.default_code
        super().__init__(detail=detail, code=code)
