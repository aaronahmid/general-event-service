from django.contrib.auth.models import AnonymousUser
from knox.models import AuthToken
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
import hashlib


@database_sync_to_async
def get_user(token_key, name):
    try:
        if name == "token":
            token = AuthToken.objects.get(token_key=token_key)
            return token.user

        else:
            tokens = AuthToken.objects.all()
            if tokens:
                for stored_token in tokens:
                    tkk = stored_token.token_key
                    stored_token_hash = hashlib.sha256(
                        str(tkk).encode("utf-8")
                    ).hexdigest()

                    if token_key == stored_token_hash:
                        token = AuthToken.objects.get(token_key=tkk)
                        return token.user

    except AuthToken.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        token_key = None

        try:
            for name, value in scope.get("headers", []):
                if name == b"authorization":
                    # -- Assuming the Authorization header is in the format "Bearer token" --
                    parts = value.decode().split()
                    if len(parts) == 2 and parts[0].lower() == "token":
                        token_key, param_name = parts[1][:8], "token"
                    break

            if token_key is None:
                raise ValueError("token not found")

        except ValueError:
            # -- Assuming the token was passed in the
            # query string '?tk=<token>' --
            token_key, param_name = (
                dict(
                    (
                        x.split("=")
                        for x in scope["query_string"].decode("utf-8").split("&")
                    )
                )
            ).get("tk", None), "tk"

        scope["user"] = (
            AnonymousUser()
            if token_key is None
            else await get_user(token_key, param_name)
        )
        return await super().__call__(scope, receive, send)


class OAuthMiddleware(BaseMiddleware):
    pass
