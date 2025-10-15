from flask import (
    Flask,
    Response,
    render_template
)
from flask_basicauth import BasicAuth
from user.user_preferences import (
    DEFAULT_MIRTO_PORT_KEY,
    DEFAULT_MIRTO_HOST_KEY,
    DEFAULT_MIRTO_PASSWORD_KEY,
    DEFAULT_MIRTO_USERNAME_KEY,
)
from controllers.routers.packet import PacketAPI
from controllers.routers.packets import PacketListAPI
from controllers.routers.rule import RuleAPI
from controllers.routers.service import ServiceAPI
from controllers.routers.services import ServicesAPI


class MirtoAPI:
    APP_USERNAME_KEY = 'BASIC_AUTH_USERNAME'
    APP_PASSWORD_KEY = 'BASIC_AUTH_PASSWORD'

    def __init__(self, process_orchestrator):
        self._process_orchestrator = process_orchestrator
        self._app = Flask(__name__)
        self._configure_app()
        self._auth = BasicAuth(self._app)
        self._routers = []
        self._add_routes()

    def _configure_app(self):
        self._app.logger = self._process_orchestrator.get_logger()

        user_pref = self._process_orchestrator.get_user_prefs()
        mirto_username = user_pref.mirto_config.get(DEFAULT_MIRTO_USERNAME_KEY)
        mirto_password = user_pref.mirto_config.get(DEFAULT_MIRTO_PASSWORD_KEY)

        self._app.config[MirtoAPI.APP_USERNAME_KEY] = mirto_username
        self._app.config[MirtoAPI.APP_PASSWORD_KEY] = mirto_password

    def _add_routes(self):
        def views_as_url_rule(apis):
            for api in apis:
                view_as_url_rule(api)

        def view_as_url_rule(api):
            view_func = api.as_view(
                api.API_NAME,
                self._auth,
                self._process_orchestrator
            )
            self._app.add_url_rule(
                api.BASE_PATH,
                view_func=view_func,
                methods=api.SUPPORTED_METHODS
            )

        self.get_status = self._app.route(
            '/status', methods=['GET']
        )(self.get_status)

        self.home = self._app.route(
            '/home', methods=['GET']
        )(self._auth.required(self.home))

        views_as_url_rule((
            ServiceAPI,
            ServicesAPI,
            PacketListAPI,
            PacketAPI,
            RuleAPI
        ))

    def run(self):
        user_pref = self._process_orchestrator.get_user_prefs()

        api_host = user_pref.mirto_config[DEFAULT_MIRTO_HOST_KEY]
        api_port = user_pref.mirto_config[DEFAULT_MIRTO_PORT_KEY]

        self._app.run(host=api_host, port=api_port)

    def get_status(self):
        return Response('OK', status=200)

    def home(self):
        return render_template("index.html")


def start_rest_api(process_orchestrator):
    api_interface = MirtoAPI(process_orchestrator)
    api_interface.run()
