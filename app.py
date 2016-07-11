import web
import os
import urllib
import requests
import logging
import jinja2
from wsgilog import WsgiLog, LOGNAME


class Log(WsgiLog):
    def __init__(self, application):
        WsgiLog.__init__(
            self,
            application,
            logformat='%(message)s',
            tostream=True,
            toprint=True,
            loglevel=logging.DEBUG
        )


LOG = logging.getLogger(LOGNAME)

urls = (
    "/", "WeixinAuthorize",
    "/weixin-redirect", "WeixinAuthentication"
)
web.config.update({"debug": True})

app = web.application(urls, globals())

WEIXIN_REDIRECT_URL = os.getenv("WEIXIN_REDIRECT_URL", "http://localhost:8080")
WEIXIN_APP_ID = os.getenv("WEIXIN_APP_ID", "wx3835b5b04b704dfe")
WEIXIN_APP_SECRET = os.getenv("WEIXIN_APP_SECRET", "9c5eaf0f1a671a6c84f27446af9966be")

weixin_auth_url = 'https://open.weixin.qq.com/connect/oauth2/authorize'
weixin_access_token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"


def build_weixin_auth_query_string(redirect_uri):
    return "{weixin_auth_url}?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_base&state=state".format(
        weixin_auth_url=urllib.quote(weixin_auth_url),
        appid=WEIXIN_APP_ID,
        redirect_uri=redirect_uri
    )


class WeixinAuthorize(object):
    def GET(self):
        redirect_url = build_weixin_auth_query_string(WEIXIN_REDIRECT_URL)
        LOG.debug("redirect url %s", redirect_url)
        raise web.Redirect(redirect_url, absolute=True)


class WeixinAuthentication(object):
    def GET(self):

        query_dict = web.input()
        if query_dict and query_dict.get("code"):
            token_info = requests.get(weixin_access_token_url,
                                      params=dict(appid=WEIXIN_APP_ID, secret=WEIXIN_APP_SECRET,
                                                  code=query_dict['code'],
                                                  grant_type="authorization_code")).json()
            # token_info = {"test": "test"}

            LOG.debug("GOT WEIXIN TOKEN %s", token_info)
            with open("daovoice_template.html", "r") as f:

                template = jinja2.Template(f.read())
                return template.render(token_dict=token_info)

        else:
            raise web.redirect("/")


if __name__ == '__main__':
    app.run(Log)
