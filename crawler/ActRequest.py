from crawler.config import TIME_OUT,REQUEST_DONE,REQUEST_ERROR
from tools.utils import logging
from crawler.config import DEFAULT_PROXY
from copy import deepcopy
import requests
logger = logging.getLogger(__name__)


class ActRequest():
    """
    执行请求动作
    """
    @staticmethod
    def act_load_more(req_data, offset, proxy=DEFAULT_PROXY):
        """
        执行加载更多历史消息请求 递归调用该函数能实现对所有历史文章的爬取
        """
        # 拷贝req_data独立存在
        data = deepcopy(req_data['load_more'])
        data['timeout'] = TIME_OUT
        data['proxy'] = proxy
        data['proxy'] = {'http':proxy,'https':proxy}
        data['url_param_dict']['offset'] = offset
        return ActRequest.act_meta_request(data)

    @staticmethod
    def act_load_all(req_data, proxy=DEFAULT_PROXY):
        """
        执行加载所有历史信息请求
        """
        data = deepcopy(req_data['load_all'])
        data['timeout'] = TIME_OUT
        data['proxy'] = {'http':proxy,'https':proxy}
        return ActRequest.act_meta_request(data)

    @staticmethod
    def act_content(req_data, url_param_dict, proxy=DEFAULT_PROXY):
        """
        获得文章的html信息
        """
        data = deepcopy(req_data['content'])
        data['url_param_dict'].update(url_param_dict)
        data['timeout'] = TIME_OUT
        data['proxy'] = {'http':proxy,'https':proxy}
        return ActRequest.act_meta_request(data)

    @staticmethod
    def act_appmsg_comment(req_data,comment_id, proxy=DEFAULT_PROXY):
        """
        执行获取评论信息请求
        """
        data = deepcopy(req_data['appmsg_comment'])
        data['url_param_dict']['comment_id'] = comment_id
        data['timeout'] = TIME_OUT
        data['proxy'] = {'http':proxy,'https':proxy}
        return ActRequest.act_meta_request(data)

    @staticmethod
    def act_getappmsgext(req_data,url_param_dict,comment_id, proxy=DEFAULT_PROXY):
        """
        执行获取阅读信息请求
        url_param_dict:文章链接中包含的url参数字典
        comment_id:该文章的评论id
        """
        # 获取参数列表要放在调用其他函数最前面
        data = deepcopy(req_data['getappmsgext'])
        data['timeout'] = TIME_OUT
        data['proxy'] = {'http':proxy,'https':proxy}
        # 根据文章真实url中的参数更新body参数
        data['body_dict'].update(url_param_dict)
        # 插入comment_id才能获取评论数据
        data['body_dict']['comment_id'] = comment_id
        # 设置为需要赞赏数量
        data['body_dict']['is_need_reward'] = 1
        return ActRequest.act_meta_request(data)

    @staticmethod
    def act_meta_request(data):
        """
        :param data:
        :return:执行一次请求的格式十分相似 通过元请求进行封装
        如果将proxy设置为127.0.0.1请求会被微信服务器积极拒绝
        正确：
        {'request':req_data+,
         'r':response,
         'i':REQUEST_DONE}
         错误：
         {'request':req_data+,'
          'e':error,
          'i':REQUEST_ERROR}
        """
        r = {}
        # 经过试验发现讲url参数和url放在一起requests更加稳定 产生新字段url_param_str\
        # 此处逻辑判断是因为频繁限制等待5分钟之后将继续爬取并使用参数r['request'] = deepcopy(data)
        if data['url_param_dict'] != {}:
            ActRequest.combine_url_and_param(data)
        # 拷贝一份请求参数往后传递如果出现错误可再次发起请求
        r['request'] = deepcopy(data)
        try:
            if data['method'] == 'GET':
                resp = requests.get(
                    url     = data['url_and_param_str'],
                    data    = data['body_dict'],
                    headers = data['headers'],
                    timeout = data['timeout'],
                    # proxies = data['proxy'],
                    verify  = False)
            if data['method'] == 'POST':
                resp = requests.post(
                    url     = data['url_and_param_str'],
                    data    = data['body_dict'],
                    headers = data['headers'],
                    timeout = data['timeout'],
                    # proxies = data['proxy'],
                    verify  = False)

            r['r'] = resp
            r['i'] = REQUEST_DONE
            return r
        except Exception as e:
            logger.error('请求 %s 发生错误...\n错误信息%s\n当前请求数据%s'%(str(data['url']),str(e),str(data)))
            r['i'] = REQUEST_ERROR
            r['e'] = e
            return r

    @staticmethod
    def combine_url_and_param(data):
        """
        经过试验发现讲url参数和url放在一起requests更加稳定
        合并之后将data['url_param_dict']设置为｛｝
        """
        url_param_str = ActRequest.dict_to_str(data['url_param_dict'])
        data['url_param_dict'] = {}
        data['url_and_param_str'] = data['url']+url_param_str
        return data['url_and_param_str']

    @staticmethod
    def dict_to_str(data, join_symbol="&", split_symbol="="):
        s = ''
        for k in data:
            s += str(k)+split_symbol+str(data[k])+join_symbol
        return s[:-2]
