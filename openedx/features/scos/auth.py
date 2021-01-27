"""SCOS user authentication module"""
import datetime
from calendar import timegm

import six

from jwkest import JWKESTException
from jwkest.jwk import KEYS
from jwkest.jws import JWS

from requests_oauthlib import OAuth1
from oauthlib.oauth1 import SIGNATURE_TYPE_AUTH_HEADER

from six.moves.urllib_parse import urlencode, unquote

from social_core.backends.base import BaseAuth
from social_core.backends.oauth import OAuthAuth
from social_core.utils import cache, url_add_parameters, \
                              parse_qs, handle_http_errors
from social_core.exceptions import AuthFailed, AuthCanceled, \
                  AuthUnknownError, AuthMissingParameter, \
                  AuthStateMissing, AuthStateForbidden, AuthTokenError

from users import add_scos_user

"""
examples:
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -d 'grant_type=password&client_id=onlineacademy&client_secret=5a04d64a-246d-4468-8929-57f439aa6fa9&username=vvandropov@fa.ru&password=Ptvkzghjof22!' "https://auth.online.edu.ru/realms/portfolio/protocol/openid-connect/token"

curl -d access_token=eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJhRGlwanZQUFV0TDEwXy11M3Y3dlhvb0dKdzBYSDJ3bk9GZDJDWjNXVEJNIn0.eyJqdGkiOiI5NGYyMTcwOC00ZWIyLTQ3NGEtYjU0YS04MTcyZDViZWRhY2UiLCJleHAiOjE2MDQwOTIyNjUsIm5iZiI6MCwiaWF0IjoxNjA0MDkxOTY1LCJpc3MiOiJodHRwczovL2F1dGgub25saW5lLmVkdS5ydS9yZWFsbXMvcG9ydGZvbGlvIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImZhZThmZmMwLWMwMzktNDUyNi1hNzE3LTk2ZjBmN2NlYTE3MiIsInR5cCI6IkJlYXJlciIsImF6cCI6Im9ubGluZWFjYWRlbXkiLCJhdXRoX3RpbWUiOjAsInNlc3Npb25fc3RhdGUiOiI1ZGFlNDZiMC0zNTVlLTQ2ZmMtYjI0Zi03OTQzMmNjMDgxYzMiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vb25saW5lLmZhLnJ1Il0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJWbGFkaW1pciBBbmRyb3BvdiIsInByZWZlcnJlZF91c2VybmFtZSI6InZ2YW5kcm9wb3ZAZmEucnUiLCJtaWRkbGVfbmFtZSI6IiIsImdpdmVuX25hbWUiOiJWbGFkaW1pciIsImZhbWlseV9uYW1lIjoiQW5kcm9wb3YiLCJlbWFpbCI6InZ2YW5kcm9wb3ZAZmEucnUifQ.DEyD0Q6LCA4a8B3VTwtTa7u3LjkdcjMCyHwxqlA2i1c15FA3OMqehYOYRY4LRKrNCB_R026CDBSNs__8mepSSjELEt1Hq6WoQBemWmhzNoXigh1R17DyGMVU3MxRD4rZhneyUv7XA2CJGriKRKDN24g5chhdP5cqCcUdeRCoHOVH0jZnTJdqrCioDZfg8rUKwmqY1L_ajJirzxUPRIqPE47R0ci62THr1yuTmIJ59q5Mv62-QWXt7GXGPLK7AiJlNJu-_NAfqUjAL32vbxFAHhQqfFivSwoVws8SrRacO8je3H2mXyUiTRRkEe3CQie-WBQyMqMqFYBWQjkcQx_Zng "https://auth.online.edu.ru/realms/portfolio/protocol/openid-connect/userinfo"

curl "https://auth.online.edu.ru/realms/portfolio/protocol/openid-connect/certs"

python /edx/app/edxapp/edx-platform/openedx/features/scos/do.py testplt status interfinance onlineacademy
"""


SSO_BASE_URL = 'https://auth.online.edu.ru/realms/portfolio'
SSO_OIDC_URL = SSO_BASE_URL	+ '/protocol/openid-connect/'
SSO_AUTH_URL = SSO_OIDC_URL + 'auth'
SSO_TOKEN_URL = SSO_OIDC_URL + 'token'
SSO_USERINFO_URL = SSO_OIDC_URL + 'userinfo'
SSO_LOGOUT_URL = SSO_OIDC_URL + 'logout'


class ScosOAuth2(OAuthAuth):
    """SCOS OAuth2 authentication implementation"""
    name = 'scos'
    CLIENT_ID = 'onlineacademy'
    CLIENT_SECRET_KEY = '5a04d64a-246d-4468-8929-57f439aa6fa9'
    REFRESH_TOKEN_URL = None
    REFRESH_TOKEN_METHOD = 'POST'
    RESPONSE_TYPE = 'code'
    REDIRECT_STATE = True
    STATE_PARAMETER = True

    def get_key_and_secret(self):
        return self.CLIENT_ID, self.CLIENT_SECRET_KEY

    def auth_params(self, state=None):
        client_id, client_secret = self.get_key_and_secret()
        params = {
            'client_id': client_id,
            'redirect_uri': self.get_redirect_uri(state)
        }
        if self.STATE_PARAMETER and state:
            params['state'] = state
        if self.RESPONSE_TYPE:
            params['response_type'] = self.RESPONSE_TYPE
        return params

    def auth_url(self):
        state = self.get_or_create_state()
        params = self.auth_params(state)
        params.update(self.get_scope_argument())
        params.update(self.auth_extra_arguments())
        params = urlencode(params)
        if not self.REDIRECT_STATE:
            params = unquote(params)
        return '{0}?{1}'.format(self.authorization_url(), params)

    def auth_complete_params(self, state=None):
        client_id, client_secret = self.get_key_and_secret()
        return {
            'grant_type': 'authorization_code',
            'code': self.data.get('code', ''),
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': self.get_redirect_uri(state)
        }

    def auth_complete_credentials(self):
        return None

    def auth_headers(self):
        return {'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'}

    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        data = super(ScosOAuth2, self).extra_data(user, uid, response,
                                                  details=details,
                                                  *args, **kwargs)
        data['token_type'] = response.get('token_type') or \
                             kwargs.get('token_type')
        return data

    def request_access_token(self, *args, **kwargs):
        return self.get_json(*args, **kwargs)

    def process_error(self, data):
        if data.get('error'):
            if data['error'] == 'denied' or data['error'] == 'access_denied':
                raise AuthCanceled(self, data.get('error_description', ''))
            raise AuthFailed(self, data.get('error_description') or
                                   data['error'])
        elif 'denied' in data:
            raise AuthCanceled(self, data['denied'])

    @handle_http_errors
    def auth_complete(self, *args, **kwargs):
        self.process_error(self.data)
        state = self.validate_state()

        response = self.request_access_token(
            self.access_token_url(),
            data=self.auth_complete_params(state),
            headers=self.auth_headers(),
            auth=self.auth_complete_credentials(),
            method=self.ACCESS_TOKEN_METHOD
        )
        self.process_error(response)
        return self.do_auth(response['access_token'], response=response,
                            *args, **kwargs)

    @handle_http_errors
    def do_auth(self, access_token, *args, **kwargs):
        data = self.user_data(access_token, *args, **kwargs)
        response = kwargs.get('response') or {}
        response.update(data or {})
        if 'access_token' not in response:
            response['access_token'] = access_token
        kwargs.update({'response': response, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)

    def refresh_token_params(self, token, *args, **kwargs):
        client_id, client_secret = self.get_key_and_secret()
        return {
            'refresh_token': token,
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret
        }

    def process_refresh_token_response(self, response, *args, **kwargs):
        return response.json()

    def refresh_token(self, token, *args, **kwargs):
        params = self.refresh_token_params(token, *args, **kwargs)
        url = self.refresh_token_url()
        method = self.REFRESH_TOKEN_METHOD
        key = 'params' if method == 'GET' else 'data'
        request_args = {'headers': self.auth_headers(),
                        'method': method,
                        key: params}
        request = self.request(url, **request_args)
        return self.process_refresh_token_response(request, *args, **kwargs)

    def refresh_token_url(self):
        return self.REFRESH_TOKEN_URL or self.access_token_url()


class ScosOidcAuthAssociation(object):
    """SCOS OIDC properties mapping"""
    def __init__(self, handle, secret='', issued=0, lifetime=0, assoc_type=''):
        self.handle = handle
        self.secret = secret.encode()
        self.issued = issued
        self.lifetime = lifetime
        self.assoc_type = assoc_type


class ScosOidcAuth(ScosOAuth2):
    """SCOS OIDC authentication implementation"""
    name = 'scos'
    OIDC_ENDPOINT = 'https://auth.online.edu.ru/realms/portfolio'
    ID_TOKEN_MAX_AGE = 600
    DEFAULT_SCOPE = ['openid', 'profile', 'email']
    EXTRA_DATA = ['id_token', 'refresh_token', ('sub', 'id')]
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_METHOD = 'GET'
    ID_KEY = 'sub'
    USERNAME_KEY = 'preferred_username'
    ID_TOKEN_ISSUER = ''
    ACCESS_TOKEN_URL = ''
    AUTHORIZATION_URL = ''
    REVOKE_TOKEN_URL = ''
    USERINFO_URL = ''
    JWKS_URI = ''

    def __init__(self, *args, **kwargs):
        self.id_token = None
        super(ScosOidcAuth, self).__init__(*args, **kwargs)

    def authorization_url(self):
        return self.AUTHORIZATION_URL or \
            self.oidc_config().get('authorization_endpoint')

    def access_token_url(self):
        return self.ACCESS_TOKEN_URL or \
            self.oidc_config().get('token_endpoint')

    def revoke_token_url(self, token, uid):
        return self.REVOKE_TOKEN_URL or \
            self.oidc_config().get('revocation_endpoint')

    def id_token_issuer(self):
        return self.ID_TOKEN_ISSUER or \
            self.oidc_config().get('issuer')

    def userinfo_url(self):
        return self.USERINFO_URL or \
            self.oidc_config().get('userinfo_endpoint')

    def jwks_uri(self):
        return self.JWKS_URI or \
            self.oidc_config().get('jwks_uri')

    @cache(ttl=86400)
    def oidc_config(self):
        return self.get_json(self.OIDC_ENDPOINT +
                             '/.well-known/openid-configuration')

    @cache(ttl=86400)
    def get_jwks_keys(self):
        keys = KEYS()
        keys.load_from_url(self.jwks_uri())

        client_id, client_secret = self.get_key_and_secret()
        keys.add({'key': client_secret, 'kty': 'oct'})
        return keys

    def auth_params(self, state=None):
        params = super(ScosOidcAuth, self).auth_params(state)
        params['nonce'] = self.get_and_store_nonce(
            self.authorization_url(), state
        )
        return params

    def get_and_store_nonce(self, url, state):
        nonce = self.strategy.random_string(64)
        association = ScosOidcAuthAssociation(nonce, assoc_type=state)
        self.strategy.storage.association.store(url, association)
        return nonce

    def get_nonce(self, nonce):
        try:
            return self.strategy.storage.association.get(
                server_url=self.authorization_url(),
                handle=nonce
            )[0]
        except IndexError:
            pass

    def remove_nonce(self, nonce_id):
        self.strategy.storage.association.remove([nonce_id])

    def validate_claims(self, id_token):
        if id_token['iss'] != self.id_token_issuer():
            raise AuthTokenError(self, 'Invalid issuer')

        client_id, client_secret = self.get_key_and_secret()

        if isinstance(id_token['aud'], six.string_types):
            id_token['aud'] = [id_token['aud']]

        if client_id not in id_token['aud']:
            raise AuthTokenError(self, 'Invalid audience')

        if len(id_token['aud']) > 1 and 'azp' not in id_token:
            raise AuthTokenError(self, 'Incorrect id_token: azp')

        if 'azp' in id_token and id_token['azp'] != client_id:
            raise AuthTokenError(self, 'Incorrect id_token: azp')

        utc_timestamp = timegm(datetime.datetime.utcnow().utctimetuple())
        if utc_timestamp > id_token['exp']:
            raise AuthTokenError(self, 'Signature has expired')

        if 'nbf' in id_token and utc_timestamp < id_token['nbf']:
            raise AuthTokenError(self, 'Incorrect id_token: nbf')

        iat_leeway = self.setting('ID_TOKEN_MAX_AGE', self.ID_TOKEN_MAX_AGE)
        if utc_timestamp > id_token['iat'] + iat_leeway:
            raise AuthTokenError(self, 'Incorrect id_token: iat')

        nonce = id_token.get('nonce')
        if not nonce:
            raise AuthTokenError(self, 'Incorrect id_token: nonce')

        nonce_obj = self.get_nonce(nonce)
        if nonce_obj:
            self.remove_nonce(nonce_obj.id)
        else:
            raise AuthTokenError(self, 'Incorrect id_token: nonce')

    def validate_and_return_id_token(self, jws):
        try:
            id_token = JWS().verify_compact(jws.encode('utf-8'),
                                            self.get_jwks_keys())
        except JWKESTException:
            raise AuthTokenError(self, 'Signature verification failed')

        self.validate_claims(id_token)

        return id_token

    def request_access_token(self, *args, **kwargs):
        response = self.get_json(*args, **kwargs)
        self.id_token = self.validate_and_return_id_token(response['id_token'])
        return response

    def user_data(self, access_token, *args, **kwargs):
        return self.get_json(self.userinfo_url(), headers={
            'Authorization': 'Bearer {0}'.format(access_token)
        })

    def get_user_details(self, response):
        username_key = self.setting('USERNAME_KEY', default=self.USERNAME_KEY)
        user_id_key = self.setting('ID_KEY', default=self.ID_KEY)

        username = response.get(username_key)
        user_id = response.get(user_id_key)

        add_scos_user(username, user_id)

        return {
            'username': response.get(username_key),
            'email': response.get('email'),
            'fullname': response.get('name'),
            'first_name': response.get('given_name'),
            'last_name': response.get('family_name'),
            'scos_id': response.get(user_id_key)
        }
