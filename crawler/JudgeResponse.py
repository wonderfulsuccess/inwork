from crawler.config import REQUEST_DONE,GET_LOAD_MORE_FREQ_ERROR,GETAPPMSGEXT_FREQ_ERROR,GETAPPMSGEXT_PARAM_ERROR,TIME_OUT_ERROR
from crawler.config import CRAWLER_DELAY
from tools.utils import logging
logger = logging.getLogger(__name__)
import time
from crawler.ActRequest import ActRequest


class JudgeResponse():
    """
    核心任务是根据ActRequest返回的r信息判断数据是否正常，如果不正常则标志错误原因方便后续程序处理
    """
    @staticmethod
    def judge_load_more(r):
        """
        可能错误类型
        GET_LOAD_MORE_FREQ_ERROR：获取历史消息达到每日限制 每日限制大约在1000到2000之间
        处理方法：更新账号继续获取历史文章列表
        """
        if r['i'] == REQUEST_DONE:
            if r['r'].json() == GET_LOAD_MORE_FREQ_ERROR:
                logger.warning('获取历史消息达到每日限制 每日限制大约在1000到2000之间，可能需要限制24小时，请更换main微信并重启')
                r['i'] = GET_LOAD_MORE_FREQ_ERROR
            return r
        else:
            return JudgeResponse.request_error_handler(r)

    @staticmethod
    def judge_getappmsgext(r):
        """
        可能错误类型
        GETAPPMSGEXT_PARAM_ERROR：若干小时后appmsg_token会过期导致无法获取阅读信息
        处理方法：重新获取请求信息
        GETAPPMSGEXT_FREQ_ERROR：请求过于频繁
        处理方法：等待5分钟继续使用原有参数请求
        """
        if r['i'] == REQUEST_DONE:
            if r['r'].json() == GETAPPMSGEXT_PARAM_ERROR:
                logger.warning('爬取阅读数据参数不对或者appmsg_token参数过期 即将重新点击')
                r['i'] = GETAPPMSGEXT_PARAM_ERROR
            elif r['r'].json() == GETAPPMSGEXT_FREQ_ERROR:
                logger.warning('爬取阅读数据过于频繁，等待5分钟')
                r['i'] = GETAPPMSGEXT_FREQ_ERROR
            return r
        else:
            return JudgeResponse.request_error_handler(r)

    @staticmethod
    def judge_load_all(r):
        """
        可能错误类型
        请求参数过期，该参数生命周期很短可能只有十几分钟
        :param r:
        :return:
        """
        if r['i'] == REQUEST_DONE:
            return r['r']
        else:
            return JudgeResponse.request_error_handler(r)

    @staticmethod
    def judge_appmsg_comment(r):
        """
        从理论上分析品论信息获取的appmsg_token也会出现过期的情况 但是由于是先请求阅读信息
        即便过期也已经被请求阅读信息出现过期行为时更新
        """
        if r['i'] == REQUEST_DONE:
            return r['r']
        else:
            return JudgeResponse.request_error_handler(r)

    @staticmethod
    def judge_content(r):
        '''
        存在IP被限制的可能性，在2秒钟的抓取频率下被限制的可能性不大，暂时不做任何处理
        如果仅仅只需获取文章内容，则可以通过多线程方式使用多个代理IP进行
        可能存在的错误
        IP被限制
        '''
        if r['i'] == REQUEST_DONE:
            return r['r']
        else:
            return JudgeResponse.request_error_handler(r)

    @staticmethod
    def request_error_handler(r):
        '''
        处理请求行为发生的错误，例如网络故障或因为代理IP的原因，尚未获得服务器的返回结果
        可能出现的错误
        TIME_OUT_ERROR:连接超时 更换IP
        NETWORK_ERROR:网络通常 检查网络
        '''
        if TIME_OUT_ERROR in str(r['e']):
            logger.error('请求超时 %s'%(str(r['e'])))
            r['i'] = TIME_OUT_ERROR

        # elif NETWORK_ERROR in str(r['e']):
        #     logger.error('网络错误 %s'%(str(r['e'])))
        #     r['i'] = NETWORK_ERROR
        return r
