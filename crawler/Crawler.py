from crawler.DecodeRequest import DecodeRequest as DR
from crawler.ActRequest import ActRequest as AR
from crawler.JudgeResponse import JudgeResponse as JR
from crawler.ProcessResponse import ProcessResponse as PR
from crawler.config import NO_REQ_DATA
from weixin_operate.WeixinOperate import WeixinOperate as WO
from proxy_admin.TidyReqData import TidyReqData as TR
import time



class PhoneCrawler(DR, AR, JR, PR, WO, TR):
    """
    该爬虫能借着手机获取公众号的所有历史文章和阅读数据速度不能太快，获取历史文章列表需要该爬虫
    定义：给微信爬虫只需要一个安卓模拟器端口号,机型和微信昵称在随后的爬取中能自动获取到
    使用：该如何使用爬虫？给一个url和需要的数据内容比如如果只要文章数据则通过代理IP多线程爬取，也可能试要使用爬虫获取文章列表
    一个爬虫自己维护一套请求参数
    """
    def __init__(self, phone, phone_model, redis):
        super(WO, self).__init__(phone=phone)
        # 记录当前正在服务公众号信息
        self.phone_model = phone_model
        self.account_info = {}
        self.redis = redis

    def get_articel_list(self, nickname, offset, args=None):
        """
        :param nickname:公众号昵称
        :param offset:历史列表消息offset
        :param args:行为控制比如offset区间 递归等信息
        :return:
        """
        # 判断是否需要更新请求参数 如果需要更新参数这将是一个耗时操作
        self.check_name(nickname,'all')
        # 根据给定的offset和args执行请求动作
        req_data = self.account_info['all_req_data']
        r = PR.process_load_more(JR.judge_load_more(AR.act_load_more(req_data,offset)))
        for key in r['r']['data']:
            for k in key:
                print(k)
            return 0
        # 返回数据

    def get_articel(self, nickname, content_url, args=None):
        """
        :param content_url:articel的永久连接 通过get_articel_list获取
        :param args:控制信息 比如需要爬取的字段
        :param nickname:公众号昵称
        :return:article信息
        """
        # 判断是否需要更新请求参数 如果需要更新参数这将是一个耗时操作
        self.check_name(nickname,'part')
        # 根据给定的offset和args执行请求动作
        print(nickname, self.account_info)
        # 返回数据

    def update_req_data(self, nickname, all_or_part):
        """
        :param all_or_part:是更新包括load_more和load_all在内的全部参数还是仅仅阅读和评论的请求参数
        :param nickname:昵称
        :return:更新爬虫需要的请求信息 请求参数自动存储在redis中 返回当前时间戳 方便比对请求参数时间
        """
        # if all_or_part == 'all':
        #     self.get_all_req_data(nickname=nickname)
        # elif all_or_part == 'part':
        #     self.get_part_req_data(nickname=nickname)
        # 整理redis中的req_data更新tidy_req_data
        TR.tidy(self.redis)
        # 调用DR将参数存入对象self.account_info中
        all_req_data = DR.get_request_data(self.phone_model,self.redis)
        self.account_info['all_req_data'] = all_req_data
        return int(time.time())

    def check_name(self,nickname,all_or_part):
        """
        :param nickname:
        :return:检查缓存的请求信息是否和当前任务公众号匹配 跟新了参数返回1 未更新参数返回0
        """
        if ('nickname' not in self.account_info) or (self.account_info['nickname'] != nickname):
            self.update_req_data(nickname,all_or_part)
            self.account_info['nickname'] = nickname
            return 1
        return 0

class ProxyCrawler():
    """
    根据PhoneCrawler获取的历史文章URL使用代理方式多线程快速获取文章内容但不包括阅读数据
    自己维护可用的代理IP和
    """
    def __init__(self):
        pass

    def ge_article(self, content_url, args):
        """
        :param content_url:articel的永久连接 通过get_articel_list获取
        :param args:控制信息
        :return:article信息 无法获取阅读信息和评论信息
        """
        pass


if __name__ == "__main__":
    import redis
    from weixin_operate.config import PHONE
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    pc1 = PhoneCrawler(phone=PHONE['PXX']['phone'],phone_model=PHONE['PXX']['phone_model'],redis=r)
    pc2 = PhoneCrawler(phone=PHONE['DRMJ']['phone'],phone_model=PHONE['DRMJ']['phone_model'],redis=r)
    # pc1.get_articel_list('新加坡眼',10)
    pc2.get_articel_list('新加坡万事通',0)
