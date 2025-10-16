from flask import jsonify, request, Response
from flask.views import MethodView
from controllers.routers.router_base import RouterBase
from objects.service import (
    Service,
    DEFAULT_SERVICE_PORT_KEY,
    DEFAULT_SERVICE_DESCRIPTION_KEY,
    DEFAULT_SERVICE_NAME_KEY,
    DEFAULT_SERVICE_TAGS_KEY,
)
from user.user_preferences import UserPreferences
from exceptions.service_not_exists import ServiceNotExists
from exceptions.duplicate_service import DuplicateServicePort
from exceptions.broken_serialized_object import BrokenSerializedObject


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

    def get(self, service_port: int) -> Response:
        try:
            user_prefs: UserPreferences = self._process_orchestrator.get_user_prefs()
            if service_port not in user_prefs.services:
                raise ServiceNotExists(service_port)
            service: Service = user_prefs.services[service_port]
            return jsonify(service.to_dict())
        except Exception as e:
            return self.client_fail(e)

    def put(self, service_port: int) -> Response:
        # TODO aggiorna il servizio
        pass

    def post(self, service_port: int) -> Response:
        try:
            service_data = request.get_json()
            service_data[DEFAULT_SERVICE_PORT_KEY] = service_port

            user_prefs: UserPreferences = self._process_orchestrator.get_user_prefs()
            if service_port in user_prefs.services:
                raise DuplicateServicePort(service_port)

            has_descr_key = DEFAULT_SERVICE_DESCRIPTION_KEY in service_data
            has_name_key = DEFAULT_SERVICE_NAME_KEY in service_data

            if not (has_descr_key and has_name_key):
                error_string = f'No {DEFAULT_SERVICE_DESCRIPTION_KEY} or {DEFAULT_SERVICE_NAME_KEY} in body'
                raise BrokenSerializedObject(error_string)

            new_service: Service = Service.from_dict(service_data)
            user_prefs.services[service_port] = new_service
            return self.OK
        except Exception as e:
            return self.client_fail(e)

    def delete(self, service_port: int) -> Response:
        try:
            user_prefs: UserPreferences = self._process_orchestrator.get_user_prefs()
            if service_port not in user_prefs.services:
                raise ServiceNotExists(service_port)
            
            del user_prefs.services[service_port]
            return self.OK
        except Exception as e:
            return self.client_fail(e)
