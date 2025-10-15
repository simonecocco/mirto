from flask import Response
from flask.views import MethodView
from controllers.routers.router_base import RouterBase


class ServiceAPI(MethodView, RouterBase):
    BASE_PATH = '/service/port/<service_port>'
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

    def get(self):
        # TODO info sul servizio
        pass

    def put(self):
        # TODO aggiorna il servizio
        pass

    def post(self):
        # TODO crea il servizio
        pass

    def delete(self):
        # TODO elimina il servizio
        pass
