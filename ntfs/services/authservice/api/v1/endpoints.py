from services.authservice.api.common.endpoints import (
    LoginAPIView,
    TokenAPIBaseClass,
    UserViewset,
    RefreshTokenView,
    DuplicateTokenView,
)


class LoginAPI(LoginAPIView):
    pass


class RefreshTokenAPI(RefreshTokenView):
    pass


class DuplicateTokenAPI(DuplicateTokenView):
    pass


class TokenAPI(TokenAPIBaseClass):
    pass


class UsersAPI(UserViewset):
    pass
