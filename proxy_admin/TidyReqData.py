import json
import collections
import re
import time
from proxy_admin.config import PHONEMODE_PTN


class TidyReqData():
    """
    anyproxy直接将截取的请求数据存放在redis中TidyReqData提供方法整理出每个手机的最新请求文件
    并且删除历史请求文件
    """
    @staticmethod
    def get_all_req_data(redis):
        """
        获取redis中所有的请求文件
        :param redis:redis实例
        :return:
        ｛'1532859861243.getappmsgext.req':dict_file,)
          '1532859861446.appmsg_comment.req':dict_file｝
        """
        unordered_req_dict = {}
        ordered_req_dict = collections.OrderedDict()
        # 遍历所有的请求文件
        for key in redis.keys("*req"):
            # 请求数据的存储行为为list
            if redis.type(key) == b'list':
                req_b_data = redis.lrange(key,0,-1)
                try:
                    req_j_data = json.loads(req_b_data[0])
                except:
                    req_j_data = str(req_b_data[0])
                    # req_j_data = req_b_data[0].decode('utf8')
                unordered_req_dict[key.decode('utf8')] = req_j_data
        # 按照时间顺序排序之后返回字典
        for key in sorted(unordered_req_dict.keys()):
            ordered_req_dict[key] = unordered_req_dict[key]
        return ordered_req_dict

    @staticmethod
    def extract_agent_info(req_dict):
        for key in req_dict:
            agent = req_dict[key]['requestOptions']['headers']['User-Agent']
            agent = re.findall(PHONEMODE_PTN,agent)[0]
            agent = agent.replace(' ','')
            req_dict[key]['phoneModel'] = agent
        return req_dict

    @staticmethod
    def combine(req_dic):
        """
        找出一个手机(账号)产生的最新请求信息
        :param req_dic:
        :return:
        ｛
        'SM-G955A':{
            'all':{'update_time':'1532859858625','req_data':{...}},
            'load_more':{'update_time':'1532859858625','req_data':{...}},
            'content':{'update_time':'1532859858625','req_data':{...}},
            'getappmsgext':{'update_time':'1532859858625','req_data':{...}},
            'appmsg_comment':{'update_time':'1532859858625','req_data':{...}}},
        'SM-N950W':{
            'all':{'update_time':'1532859858625','req_data':{...}},
            'load_more':{'update_time':'1532859858625','req_data':{...}},
            'content':{'update_time':'1532859858625','req_data':{...}},
            'getappmsgext':{'update_time':'1532859858625','req_data':{...}},
            'appmsg_comment':{'update_time':'1532859858625','req_data':{...}}},
        }
        """
        tidy_req_dic = {}
        # 建立手机型号索引
        for key in req_dic:
            phoneModel = req_dic[key]['phoneModel']
            tidy_req_dic[phoneModel] = {}
        # 为每个手机型号下的数据预留数据类型
        for phoneModel in tidy_req_dic:
            tidy_req_dic[phoneModel] = {}
        # 组织all_req_data数据
        for key in req_dic:
            key_info = key.split('.')
            # 获取一次请求数据中的元信息
            timestamp = int(key_info[0])
            _type = key_info[1]
            phoneModel = req_dic[key]['phoneModel']
            req_dic[key].pop('phoneModel')
            req_data = req_dic[key]

            # 构造一部手机的模拟请求数据结构
            # 重点关注的是all_req_data部分
            all_req_data = tidy_req_dic[phoneModel]
            # 该种类型的请求数据尚未出现
            if _type not in all_req_data:
                all_req_data[_type] = {}
                all_req_data[_type]['update_time'] = timestamp
                all_req_data[_type]['req_data'] = req_data
            # 该种类型的请求数据已经存在根据timetamp和update_time的对比确定是否需要覆盖
            else:
                if timestamp > all_req_data[_type]['update_time']:
                    all_req_data[_type]['update_time'] = timestamp
                    all_req_data[_type]['req_data'] = req_data
        return tidy_req_dic

    @staticmethod
    def tidy(redis):
        """
        对redis中的请求数据整理归纳，找出每台手机最新的请求数据
        :param redis:redis实例 db必须和proxy server存放的db相同
        :return:数据格式见combine 一方面返回字典另一方方面存入redis
        """
        req_dict = TidyReqData.get_all_req_data(redis)
        req_dict = TidyReqData.extract_agent_info(req_dict)
        tidy_req_data = TidyReqData.combine(req_dict)
        # 添加更新时间戳
        tidy_req_data['update_time'] = int(time.time())
        redis.set('tidy_req_data',tidy_req_data)
        return tidy_req_data

if __name__ == '__main__':
    import redis
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    tidy_req_data = TidyReqData.tidy(r)
    print(tidy_req_data)

