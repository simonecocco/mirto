from flask import request, Response
from flask.views import MethodView
from controllers.routers.router_base import RouterBase


class RuleAPI(MethodView, RouterBase):
    BASE_PATH = '/rule'
    SUPPORTED_METHODS = ['GET', 'POST']
    API_NAME = 'rule_api'

    def __init__(self, auth, process_orchestrator):
        super().__init__(RuleAPI.API_NAME, process_orchestrator)
        self._auth = auth
        self._configure_auth()

    def _configure_auth(self):
        self.get = self._auth.required(self.get)
        self.post = self._auth.required(self.post)

    def get(self):
        # TODO
        pass

    def post(self):
        # TODO
        pass
