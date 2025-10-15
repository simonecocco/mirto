from flask import Response
from flask.views import MethodView
from controllers.routers.router_base import RouterBase
from json import dumps
from typing import List
from objects.service import Service
from user.user_preferences import UserPreferences


class ServicesAPI(MethodView, RouterBase):
    BASE_PATH = '/services'
    SUPPORTED_METHODS = ['GET']
    API_NAME = 'services_api'

    def __init__(self, auth, process_orchestrator):
        super().__init__(ServicesAPI.API_NAME, process_orchestrator)
        self._auth = auth
        self._configure_auth()

    def _configure_auth(self):
        self.get = self._auth.required(self.get)

    def get(self):
        user_prefs: UserPreferences = self._process_orchestrator.get_user_prefs()
        services: List[Service] = user_prefs.services
        return Response(
            dumps([service.to_dict() for service in services]),
            status=200,
            mimetype='application/json'
        )
