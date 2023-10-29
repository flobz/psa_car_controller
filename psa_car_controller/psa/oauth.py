import logging
from http import HTTPStatus
from typing import Optional

from oauth2_client.credentials_manager import CredentialManager, ServiceInformation
from requests import Response, RequestException

from psa_car_controller.common.utils import rate_limit
from psa_car_controller.psa import connected_car_api
from psa_car_controller.psa.connected_car_api import ApiClient
from psa_car_controller.psa.connected_car_api.rest import ApiException

logger = logging.getLogger(__name__)


class OpenIdCredentialManager(CredentialManager):
    def __init__(self, service_information: ServiceInformation, proxies: Optional[dict] = None):
        super().__init__(service_information, proxies)
        self.refresh_callbacks = []

    def _grant_password_request_realm(self, login: str, password: str, realm: str) -> dict:
        return {"grant_type": 'password', "username": login, "scope": ' '.join(self.service_information.scopes),
                "password": password, "realm": realm}

    def init_with_user_credentials_realm(self, login: str, password: str, realm: str):
        self._token_request(self._grant_password_request_realm(login, password, realm), True)

    @staticmethod
    def _is_token_expired(response: Response) -> bool:
        if response.status_code == HTTPStatus.UNAUTHORIZED.value:
            logger.info("token expired, renew")
            try:
                json_data = response.json()
                return json_data.get('moreInformation') == 'Token is invalid'
            except ValueError:
                return False
        else:
            return False

    @property
    def access_token(self):
        return self._access_token

    @rate_limit(6, 1800)
    def refresh_token_now(self):
        try:
            self._refresh_token()
            for refresh_callback in self.refresh_callbacks:
                refresh_callback()
            return True
        except RequestException as e:
            logger.error("Can't refresh token %s", e)
        return False


class Oauth2PSACCApiConfig(connected_car_api.Configuration):
    def __init__(self):
        super().__init__()
        self.refresh_callback = lambda: True

    def set_refresh_callback(self, callback):
        self.refresh_callback = callback


class OauthAPIClient(ApiClient):
    # pylint: disable=no-member,too-many-arguments
    def call_api(self, resource_path, method,
                 path_params=None, query_params=None, header_params=None,
                 body=None, post_params=None, files=None,
                 response_type=None, auth_settings=None, async_req=None,
                 _return_http_data_only=None, collection_formats=None,
                 _preload_content=True, _request_timeout=None):
        for _ in range(0, 2):
            try:
                if not async_req:
                    return self._ApiClient__call_api(resource_path, method,
                                                     path_params, query_params, header_params,
                                                     body, post_params, files,
                                                     response_type, auth_settings,
                                                     _return_http_data_only, collection_formats,
                                                     _preload_content, _request_timeout)
                return self.pool.apply_async(self.__call_api, (resource_path,
                                                               method, path_params, query_params,
                                                               header_params, body,
                                                               post_params, files,
                                                               response_type, auth_settings,
                                                               _return_http_data_only,
                                                               collection_formats,
                                                               _preload_content, _request_timeout))
            except ApiException as e:
                if e.reason == 'Unauthorized':
                    self.configuration.refresh_callback()
                else:
                    raise e
        return None
