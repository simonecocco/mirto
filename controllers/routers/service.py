from flask import jsonify
from flask.views import MethodView
from controllers.routers.router_base import RouterBase
from objects.service import Service
from user.user_preferences import UserPreferences
from exceptions.service_not_exists import ServiceNotExists


class ServiceAPI(MethodView, RouterBase):
    BASE_PATH = '/service/port/<int:service_port>'
    SUPPORTED_METHODS = ['GET', 'PUT', 'POST', 'DELETE']
    API_NAME = 'service_api'

    def __init__(self, auth, process_orchestrator):
        super().__init__(ServiceAPI.API_NAME, process_orchestrator)
        self._auth = auth
        self._configure_auth()

    def _configure_auth(self):
        self.get = self._auth.required(self.get)
        self.put = self._auth.required(self.put)
        self.post = self._auth.required(self.post)
        self.delete = self._auth.required(self.delete)

    def get(self, service_port: int):
        try:
            user_prefs: UserPreferences = self._process_orchestrator.get_user_prefs()
            if service_port not in user_prefs.services:
                raise ServiceNotExists(service_port)
            service: Service = user_prefs.services[service_port]
            return jsonify(service.to_dict())
        except Exception as e:
            return self.client_fail(e)

    def put(self, service_port):
        # TODO aggiorna il servizio
        pass

    def post(self):
        # TODO crea il servizio
        pass

    def delete(self, service_port):
        try:
            user_prefs: UserPreferences = self._process_orchestrator.get_user_prefs()
            if service_port not in user_prefs.services:
                raise ServiceNotExists(service_port)
            
            del user_prefs.services[service_port]
            return self.OK
        except Exception as e:
            return self.client_fail(e)
