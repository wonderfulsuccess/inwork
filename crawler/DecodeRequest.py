from crawler.config import TIDY_REQ_DATA_KEY, NO_REQ_DATA
import ast


class DecodeRequest():
    """
    从redis获取准备好的请求数据
    """
    @staticmethod
    def get_request_data(phone_model, redis):
        """
        :param phone_model:手机型号
        :return:已经获取的属于该手机型号的请求数据 整理成方便requests使用的格式 同时方便修改请求参数
        """
        # byte to string
        tidy_req_data = redis.get(TIDY_REQ_DATA_KEY).decode('utf8')
        # string to dict
        tidy_req_data = ast.literal_eval(tidy_req_data)
        if phone_model in tidy_req_data:
            all_raw_req_data = tidy_req_data[phone_model]
            for key in all_raw_req_data:
                all_raw_req_data[key] = DecodeRequest.req_to_dict(all_raw_req_data[key]['req_data'])
            return all_raw_req_data
        else:
            return NO_REQ_DATA


    @staticmethod
    def req_to_dict(raw_req_data):
        """
        :param data:_type['req_data'] 它只是5种请求数据的一种
        :return:将anyproxy获取的req文件内容解析成为request参数所需要的字典
        """
        req_data = {}
        url_lsit = raw_req_data['url'].split('?')
        url = url_lsit[0]+'?'
        req_data['url'] = url
        req_data['method'] = raw_req_data['requestOptions']['method']
        req_data['headers'] = raw_req_data['requestOptions']['headers']
        body_str = raw_req_data['requestData']
        body_dict = DecodeRequest.str_to_dict(body_str, "&", "=")
        url_param_str = url_lsit[1]
        url_param_dict = DecodeRequest.str_to_dict(url_param_str, "&", "=")
        req_data['body_dict'] = body_dict
        req_data['url_param_dict'] = url_param_dict
        # 添加一个测试字段
        req_data['url_param_str'] = url_param_str

        return req_data

    @staticmethod
    def str_to_dict(s, join_symbol="\n", split_symbol=":"):
        """
        key与value通过split_symbol连接， key,value 对之间使用join_symbol连接
        例如： a=b&c=d   join_symbol是&, split_symbol是=
        :param s: 原字符串
        :param join_symbol: 连接符
        :param split_symbol: 分隔符
        :return: 字典
        """
        s_list = s.split(join_symbol)
        data = dict()
        for item in s_list:
            item = item.strip()
            if item:
                k, v = item.split(split_symbol, 1)
                data[k] = v.strip()
        return data

if __name__ == '__main__':
    import redis
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    req_data = DecodeRequest.get_request_data('SM-G955A',r)
    print(req_data)
