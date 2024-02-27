from aiohttp import web

from models import init_orm
from view_user_adv import UserView, LoginView, AdvView
from middleware_errors import errors_middleware, session_middleware


def _get_app() -> web.Application:
    app = web.Application()
    app.middlewares.extend([errors_middleware, session_middleware])
    app.cleanup_ctx.append(init_orm)

    app.add_routes(
        [
            web.post("/login", LoginView),
            web.get("/user/{user_id:\d+}", UserView),
            web.post("/user", UserView),
            web.patch("/user/{user_id:\d+}", UserView),
            web.delete("/user/{user_id:\d+}", UserView),
            web.get("/adv", AdvView),
            web.get("/adv/{adv_id:\d+}", AdvView),
            web.post("/adv", AdvView),
            web.patch("/adv/{adv_id:\d+}", AdvView),
            web.delete("/adv/{adv_id:\d+}", AdvView),
        ]
    )

    return app


async def get_app():
    return _get_app()

if __name__ == "__main__":
    web.run_app(_get_app())