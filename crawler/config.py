'''
decode_request
'''
# 代理服务器产生的请求文件地址
TIDY_REQ_DATA_KEY = 'tidy_req_data'
#指定的手机型号没有req data
NO_REQ_DATA = '该手机尚未发起任务请求'

'''
decode_response
'''

'''
judge_response
'''
# 请求超时代理IP 和 物理网络均有可能
TIME_OUT_ERROR = 'Read timed out'
# getappmsgext请求频繁 需要等待5分钟
GETAPPMSGEXT_FREQ_ERROR = {"base_resp":{"ret":301,"errmsg":"default"}}
# getappmsgext请求参数不对 需要重新点击 直到成功 其中就包括了appmsg_token参数过期的问题
GETAPPMSGEXT_PARAM_ERROR = {'advertisement_info': [], 'reward_head_imgs': []}
# 加载历史消息请求参数过期 生命周几可能只有10分钟
GET_LOAD_ALL_OUT_OF_DATE = "失效的验证页面"
# 加载跟多历史消息错误
GET_LOAD_MORE_ERROR = {'base_resp': {'ret': -3, 'errmsg': 'no session', 'cookie_count': 1}, 'ret': -3, 'errmsg': 'no session', 'cookie_count': 1}
# 获取历史消息达到每日限制 每日限制大约在1000到2000之间，可能需要限制24小时，请更换main微信并重启
GET_LOAD_MORE_FREQ_ERROR = {'ret': -6, 'errmsg': 'unknown error'}


'''
act_request
'''
TIME_OUT = 10 #requests请求超时时间
REQUEST_DONE = "请求完成" # 请求完成
REQUEST_ERROR = "请求时出现错误" # 请求出现错误
REQUEST_SELF_ERROR = "执行请求本身发生错误 一般发生在网络不同请求超时或者代理IP无效"
DEFAULT_PROXY = '127.0.0.1:1080'
'''
process_response
'''
# 获取文章阅读信息的间隔时间
CRAWLER_DELAY = 2.0
CRAWLER_FINISHED = "所有文章爬取完毕"


TEST_MODE = False
