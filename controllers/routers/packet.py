from flask import request, Response
from flask.views import MethodView
from controllers.routers.router_base import RouterBase


class PacketAPI(MethodView, RouterBase):
    BASE_PATH = '/packet/<packet_id>'
    SUPPORTED_METHODS = ['GET', 'PUT', 'DELETE']
    API_NAME = 'packet_api'

    def __init__(self, auth, process_orchestrator):
        super().__init__(PacketAPI.API_NAME, process_orchestrator)
        self._auth = auth
        self._configure_auth()

    def _configure_auth(self):
        self.get = self._auth.required(self.get)
        self.put = self._auth.required(self.put)
        self.delete = self._auth.required(self.delete)

    def get(self):
        # TODO ottiene i dettagli di un pacchetto
        pass

    def put(self):
        # TODO inserisce dei tag
        pass

    def delete(self):
        # TODO elimina un pacchetto in particolare
        pass