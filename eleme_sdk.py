from sdk.oauth.oauth_client import OAuthClient
from sdk.apis.shop_service import ShopService
from sdk.config import Config

config = Config(True, key, secret, call_back_url)


# 自己的日志处理方式,必须有info 和error 方法
class MyLog:
    def info(self, log):
        print(u"my info log:{}".format(log))

    def error(self, log):
        print(u"my error log:{}".format(log))


config.set_log(MyLog())
oauth_client = OAuthClient(config)