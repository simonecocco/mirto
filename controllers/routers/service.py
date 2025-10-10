from flask import Response
from flask.views import MethodView


# '/service/port/{service_port}'
class ServiceAPI(MethodView):
    def __init__(self, auth):
        self._auth = auth

    @self._auth.required
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
