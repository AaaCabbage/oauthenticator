# oauthenticator
oauthenticator for connect jupyterhub and django

this oauthenticator depends on JupyterHub Authenticator

**Installation**

clone the repo:

```
git clone https://github.com/jupyterhub/oauthenticator.git
copy the django.py to oauthenticator/oauthenticator/
cd oauthenticator
pip3 install -e .
```

**Setup**

First, you'll need to create a [Django Application](http://django-oauth-toolkit.readthedocs.io/en/latest/tutorial/tutorial_01.html#create-an-oauth2-client-application). Make sure the callback URL is:

```http[s]://[your-host]/hub/oauth_callback
http[s]://[your-host]/hub/oauth_callback
```

Where [your-host] is where your server will be running. Such as example.com:8080.

Then, add the following to your jupyterhub_config.py file:

```
c.JupyterHub.authenticator_class = 'oauthenticator.LocalDjangoOAuthenticator'
```

You will additionally need to specify the OAuth callback URL, the client ID, and the client secret (you should have gotten these when you created your OAuth app on Django server). For example, if these values are in the environment variables $OAUTH_CALLBACK_URL, $GITHUB_CLIENT_ID and $GITHUB_CLIENT_SECRET, you should add the following to your jupyterhub_config.py:

```
c.DjangoOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.DjangoOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.DjangoOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']
```

You can use your own Github Enterprise instance by setting the GITHUB_HOST environment flag.