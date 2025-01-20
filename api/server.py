import tornado
from api.services import PGManager, AuthorizationService
from api.common.vigilante import Vigilante
from api.services.emitter import Emitter

from api.routes import get_routes

pg = PGManager()
vigilante = Vigilante("analysis", log_in_file=True, directory="logs")
emitter = Emitter(vigilante)

authorization_service = AuthorizationService(pg, vigilante)

routes = get_routes(
    dict(
        pg=pg,
        vigilante=vigilante,
        authorization_service=authorization_service,
        emitter=emitter,
        auth_enabled=True,
    )
)

application = tornado.web.Application(routes)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
