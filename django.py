import json
import os
import sys

from tornado.auth import OAuth2Mixin
from tornado import gen, web

from tornado.httputil import url_concat
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

from jupyterhub.auth import LocalAuthenticator

from .oauth2 import OAuthLoginHandler, OAuthenticator

# Support django with django-oauth-toolkit
DJANGO_HOST = os.environ.get('DJANGO_HOST') or 'localhost'
DJANGO_API = '%s/api/v1/user' % DJANGO_HOST

class DjangoMixin(OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = "%s/oauth2/authorize" % DJANGO_HOST
    _OAUTH_ACCESS_TOKEN_URL = "%s/oauth2/token" % DJANGO_HOST


class DjangoLoginHandler(OAuthLoginHandler, DjangoMixin):
    pass


class DjangoOAuthenticator(OAuthenticator):

    login_service = "Django"

    client_id_env = 'DJANGO_CLIENT_ID'
    client_secret_env = 'DJANGO_CLIENT_SECRET'
    login_handler = DjangoLoginHandler

    @gen.coroutine
    def authenticate(self, handler, data=None):
        code = handler.get_argument("code", False)
        if not code:
            raise web.HTTPError(400, "oauth callback made without a token")
        # TODO: Configure the curl_httpclient for tornado
        http_client = AsyncHTTPClient()

        # Exchange the OAuth code for a django Access Token
        #
        # See: https://github.com/AaaCabbage/oauthenticator/blob/master/README.md

        # 
        params = dict(
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code,
            grant_type="authorization_code",
            redirect_uri=self.oauth_callback_url
        )

        url = url_concat("%s/oauth2/token/" % DJANGO_HOST,
                         params)
        print('=========================*******===========================')
        print(url, file=sys.stderr)

        req = HTTPRequest(url,
                          method="POST",
                          headers={"Accept": "application/json"},
                          body='' # Body is required for a POST...
                          )

        resp = yield http_client.fetch(req)
        resp_json = json.loads(resp.body.decode('utf8', 'replace'))

        access_token = resp_json['access_token']

        # Determine who the logged in user is
        headers={"Accept": "application/json",
                 "User-Agent": "JupyterHub",
        }
        req = HTTPRequest("%s?access_token=%s" % (DJANGO_API, access_token),
                          method="GET",
                          headers=headers
                          )
        resp = yield http_client.fetch(req)
        resp_json = json.loads(resp.body.decode('utf8', 'replace'))

        return resp_json["username"]


class LocalDjangoOAuthenticator(LocalAuthenticator, DjangoOAuthenticator):

    """A version that mixes in local system user creation"""
    pass