from flask import request, Response
from flask.views import MethodView


class PacketAPI(MethodView):
    def __init__(self):
        pass

    def get(self):
        # TODO ottiene i dettagli di un pacchetto
        pass

    def put(self):
        # TODO inserisce dei tag
        pass

    def delete(self):
        # TODO elimina un pacchetto in particolare
        pass