from flask import request, Response
from flask.views import MethodView


# '/packets'
class PacketListAPI(MethodView):
    def __init__(self):
        pass

    def get(self):
        # TODO ritorna i vari pacchetti
        pass

    def post(self):
        # TODO upload di un file PCAP e analisi di esso
        pass
