from flask import request, Response
from flask.views import MethodView
from controllers.routers.router_base import RouterBase


class PacketListAPI(MethodView, RouterBase):
    BASE_PATH = '/packets'
    SUPPORTED_METHODS = ['GET', 'POST']
    API_NAME = 'packets_api'

    def __init__(self, auth, process_orchestrator):
        super().__init__(PacketListAPI.API_NAME, process_orchestrator)
        self._auth = auth
        self._configure_auth()

    def _configure_auth(self):
        self.get = self._auth.required(self.get)
        self.post = self._auth.required(self.post)

    def get(self):
        # TODO ritorna i vari pacchetti
        pass

    def post(self):
        # TODO upload di un file PCAP e analisi di esso
        pass
