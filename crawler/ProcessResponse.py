from crawler.config import REQUEST_DONE
from tools.utils import logging
logger = logging.getLogger(__name__)
from datetime import datetime
import html
import json
import ast


def request_error(func):
    """
    :param func:
    :return:统一向后传递失败的请求
    """
    def wrapper(*args,**kwargs):
        r = args[0]
        if r['i'] != REQUEST_DONE:
            return r
        return func(*args,**kwargs)
    return wrapper


class ProcessResponse():
    """
    对正确返回的数据进行预处理如果遇到错误信息直接向传递
    """

    @staticmethod
    @request_error
    def process_load_more(r):
        """
        :param r:r
        :return:提取文章列表信息并且分类主副
            r['r']['data']: title,digest,content_url,source_url,cover,author,mov,p_date,id
            r['r']['des']: can_msg_continue,next_offset
        """
        use_data = {}
        use_data['data'] = []
        use_data['des'] = {}
        use_data['id'] = 0

        data = r['r'].json()
        # 添加本次获取列表之后是否可以继续以及下一个offset
        use_data['des']['can_msg_continue'] = data['can_msg_continue']
        use_data['des']['next_offset'] = data['next_offset']
        data = ast.literal_eval(data['general_msg_list'])
        # 解析消息列表
        for msg in data['list']:
            p_date = msg.get("comm_msg_info").get("datetime")
            msg_info = msg.get("app_msg_ext_info")  # 非图文消息没有此字段
            if msg_info:
                mov = 10
                msg_info['mov'] = str(mov)
                ProcessResponse._insert(use_data, msg_info, p_date)
                multi_msg_info = msg_info.get("multi_app_msg_item_list")
                for msg_item in multi_msg_info:
                    mov += 1
                    msg_item['mov'] = str(mov)
                    ProcessResponse._insert(use_data, msg_item, p_date)
            else:
                logger.warning(u"此消息不是图文推送，data=%s" % json.dumps(msg.get("comm_msg_info")))
        use_data.pop('id')
        r['r'] = use_data
        return r

    @staticmethod
    @request_error
    def process_load_all(r):
        """
        :param r:
        :return:提取出公众号的主页信息
        """
        return r

    @staticmethod
    @request_error
    def process_getappmsgext(r):
        """
        :param r:r
        :return: 提取阅读信息
        """
        r['r'] = r['r'].json()
        return r

    @staticmethod
    @request_error
    def process_content(r):
        """
        :param r:r
        :return:文章正文以及必要NLP预处理 获取comment_id
        """
        return r

    @staticmethod
    @request_error
    def process_appmsg_comment(r):
        """
        :param r:r
        :return: 整理评论信息
        """
        r['r'] = r['r'].json()
        return r

    def _insert(use_data, item, p_date):
        '''
        文章列表信息插入use_data
        '''
        use_data['id'] += 1
        keys = ('title', 'author', 'content_url', 'digest', 'cover', 'source_url','mov')
        sub_data = ProcessResponse.sub_dict(item, keys)
        p_date = datetime.fromtimestamp(p_date)
        sub_data["p_date"] = p_date
        sub_data["id"] = use_data['id']
        use_data['data'].append(sub_data)
        logger.info('%d %s %s'%(sub_data["id"],sub_data["mov"], sub_data["title"]))

    @staticmethod
    def sub_dict(d, keys):
        return {k: html.unescape(d[k]) for k in d if k in keys}

if __name__ == '__main__':
    print(ProcessResponse.process_load_more({'i':REQUEST_DONE}))
