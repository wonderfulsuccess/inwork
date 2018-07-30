from os import system
import random
from functools import wraps


def connect_phone(func):
    """
    装饰器负责每次命令前连接手机
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        system('adb connect '+args[0].phone)
        return func(*args, **kwargs)
    return wrapper


class PhoneControl():
    def __init__(self, phone):
        """
        :param phone:adb 操作手机所需要的端口信息
        """
        self.phone = phone

    def get_phone(self):
        """
        获取实例手机端口信息
        """
        return self.phone

    @connect_phone
    def get_screen_cap(self, file_name='screen_cap'):
        """
        获取截图
        """
        system('adb -s '+str(self.phone)+' shell screencap -p /sdcard/'+file_name+'.png')
        system('adb -s '+str(self.phone)+' pull /sdcard/'+file_name+'.png'+' ./'+file_name+'.png')
        return file_name+'.png'

    @connect_phone
    def input_tap(self, pos):
        """
        点击屏幕
        pos为一个区域的左上与右下坐标
        如果事先已经随机化了pos可以只是一个点 随机点击一个位置是为防止被被认为是机器人
        返回实际点击位置
        """
        if len(pos) == 2:_pos = pos
        else : _pos = (random.randint(pos[0],pos[2]),random.randint(pos[1],pos[3]))
        command = r'adb -s '+str(self.phone)+' shell input tap {} {}'.format(_pos[0],_pos[1])
        system(command)
        return _pos

    @connect_phone
    def input_swipe(self, x1, x2):
        """
        从一个位置滑动到另一位置
        :param x1:起始坐标，屏幕左上角为原点
        :param x2:终点坐标，屏幕左上角为原点
        :return:[x1,x2]
        """
        command = r'adb -s '+str(self.phone)+' shell input swipe {} {} {} {}'.format(x1[0],x1[1],x2[0],x2[1])
        system(command)
        return [x1,x2]

    @connect_phone
    def input_roll(self, dx=0, dy=500):
        """
        拉动屏幕
        :param dx:x方向速度
        :param dy:y方向速度
        :return:[dx, dy]
        """
        command = r'adb -s '+str(self.phone)+' shell input roll {} {}'.format(dx,dy)
        system(command)
        return [dx,dy]

    @connect_phone
    def input_key_event(self, event_cmd):
        """
        按键事件 比如home menue back volum_up volum_down等等 具体定义在配置文件中
        :param event_cmd:事件ID
        :return:event_cmd
        """
        command = r'adb -s '+str(self.phone)+' shell input keyevent '+event_cmd
        system(command)
        return event_cmd

    @connect_phone
    def input_text(self, text):
        """
        输入文本信息 可能不支持中文输入
        :param text:待输入的文本信息
        :return:文本信息
        """
        command = r'adb -s '+str(self.phone)+' shell input text {}'.format(text)
        system(command)
        return text

if __name__ == '__main__':
    from vc.config import KEY
    pc = PhoneControl('127.0.0.1:62001')
    pc.input_key_event(KEY['BACK_KEYEVENT'])
