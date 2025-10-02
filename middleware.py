from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.server.dependencies import get_http_headers
from fastmcp.exceptions import InvalidSignature
import os
from notion_client import Client

class UserAuthMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        headers = get_http_headers()

        if not headers:
            raise InvalidSignature("Unauthorized")

        auth_header = headers.get("authorization", None)

        if not auth_header:
            raise InvalidSignature("Unauthorized")

        user_token = auth_header.split(" ")[1]

        notion = Client(auth=user_token)
        context.fastmcp_context.set_state("notion", notion)
        context.fastmcp_context.set_state("github_token", user_token)


        return await call_next(context)
