from vc.VC import VC
from weixin_operate.config import BTN, CROP_RANGE, UI_WORDS
from vc.config import KEY
import time
from tools.utils import to_pinyin
from random import randint


class WeixinOperate(VC):
    """
    实现对微信手机app操作的自动化
    """
    def __init__(self, phone):
        super(VC, self).__init__(phone=phone)
        # 位置信息
        self.home_weixin = {} #桌面微信位置
        self.main_bottom = {} #微信主界面底部四大按钮位置
        self.gzh_folder = {} #公众号文件夹位置

    def home(self):
        """
        :return:通过多次点击BACK按键回到主界面 之所以不直接点击HOME按键 是需要层层返回微信到主界面
        """
        for i in range(7):
            self.input_key_event(KEY['BACK_KEYEVENT'])
        return 0

    def home_to_gzh_search(self):
        """
        :return:从主界面到公众号搜索
        """
        # 点击微信图标
        self.click_by_loc(BTN['EMU_WEIXIN_ICON'])
        time.sleep(0.5)
        # 点击通信录
        self.click_by_loc(BTN['TONGXUNLU_BTN'])
        time.sleep(0.5)
        # 点击公众号
        self.click_by_loc(BTN['GZH_FOLDER'])
        time.sleep(0.5)
        # 点击搜索
        self.click_by_loc(BTN['SEARCH_BTN'])
        return 0

    def search_gzh(self, nickname):
        """
        :param nickname:待搜索公众号名称
        :return:
        """
        # 汉字转拼音
        nickname_py = to_pinyin(nickname)
        # 输入拼音
        self.input_text(nickname_py)
        time.sleep(0.5)
        # 进入账号
        self.click_by_words(nickname)
        time.sleep(0.5)
        #键入主界面
        self.click_by_loc(BTN['PROFILE_BTN'])
        time.sleep(0.5)
        # 上拉
        self.input_roll()
        time.sleep(0.5)
        return 0

    def all_message(self):
        """
        :return:从公众号主页下拉点击全部消息消息
        """
        # 全部消息
        self.click_by_words('全部消息')
        # 证书确认两次 为防止点击到图片 导致接下来可能得不到评论请求数据 先做判断
        for i in range(2):
            ui_words_str = self.get_ui_words(location=False,in_str=True,crop=CROP_RANGE['CAR_NOTE'])
            if UI_WORDS['CAR_NOTE'] in ui_words_str:
                self.click_by_loc(BTN['CAR_NOTE_CONTINUE'])
            time.sleep(1) #OCR API 可能并不支持并发 降低速度比较保险
        # 上拉刷出load_more 并且等待一段时间保证收到请求参数
        self.input_roll()
        time.sleep(2)
        return 0

    def click_a_message(self, args=2):
        """
        :return:来到历史列表之后随机点击一篇文章
        """
        #获取界面文章标题消息
        if args==1:corp = CROP_RANGE['PROFILE_MESSAGE_LIST']
        elif args==2:corp = CROP_RANGE['MESSAGE_LIST']
        ui_words = self.get_ui_words(location=True, crop=corp)
        #随便点一个标题
        random_index = randint(1,len(ui_words))-1
        loc = ui_words[random_index]['location']
        pos = [loc['left'],loc['top'],loc['left']+loc['width'],loc['top']+loc['height']]
        self.click_by_loc(pos)
        # 证书确认两次 为防止点击到图片 导致接下来可能得不到评论请求数据 先做判断
        for i in range(2):
            ui_words_str = self.get_ui_words(location=False,in_str=True,crop=CROP_RANGE['CAR_NOTE'])
            if UI_WORDS['CAR_NOTE'] in ui_words_str:
                print('点击证书...')
                self.click_by_loc(BTN['CAR_NOTE_CONTINUE'])
            time.sleep(1) #OCR API 可能并不支持并发 降低速度比较保险
        #等待页面加载完毕
        time.sleep(2)

    def check_comments(self):
        """
        :return:成功打开一篇文章之后 拉到底检查评论信息
        """
        # 拉到底
        for i in range(2):
            self.input_roll()
            time.sleep(1)
        # 检查有无评论 有评论 无评论 有广告 三种情况
        ui_words_str = self.get_ui_words(location=False,in_str=True,crop=CROP_RANGE['LEAVE_MSG_BOTTOM'])
        # 如果暂无评论点击了留言按钮
        if UI_WORDS['NO_LEAVING_MSG'] in ui_words_str:
            print('点击了留言信息。。。')
            self.click_by_loc(BTN['LEAVE_MSG'])
            time.sleep(1)
            self.input_key_event(KEY['BACK_KEYEVENT'])

    def get_all_req_data(self, nickname):
        """
        获取关于一个公众号的全部请求数据 当前程序使用baidu API受到网络和并发限制效果并十分理想
        :param nickname: 公众号昵称
        :return:最后成功与否取决在redis中是否找到有有效数据
        """
        self.home()
        self.home_to_gzh_search()
        self.search_gzh(nickname)
        self.all_message()
        self.click_a_message()
        self.check_comments()
        self.home()

    def get_part_req_data(self, nickname):
        """
        仅获取阅读量和评论的请求数据
        :param nickname:公众号昵称
        :return:最后成功与否取决在redis中是否找到有有效数据
        """
        self.home()
        self.home_to_gzh_search()
        self.search_gzh(nickname)
        self.click_a_message(args=1)
        self.check_comments()
        self.home()

if __name__ == "__main__":
    wo1 = WeixinOperate('127.0.0.1:62001')
    wo1.get_part_req_data('新加坡万事通')
    wo2 = WeixinOperate('127.0.0.1:62025')
    wo2.get_all_req_data('新加坡万事通')
