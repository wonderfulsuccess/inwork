# 将图片转化为文字和像素位置信息
from aip import AipOcr
from vc.config import APP_ID, API_KEY, SECRET_KEY
from vc.config import OCR_NO_WORDS
from PIL import Image

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


class OCR():
    @staticmethod
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    @staticmethod
    def pre_process_img(pic_file_name, quality=50, crop=None):
        """
        对待上传的图片进行压缩处理
        :param pic_file_name:文件名称
        :param quality:质量百分数
        :param crop:(left, top, right, bottom)裁剪左上角和右下角的绝对坐标
        :return:
        """
        im = Image.open(pic_file_name)
        rgb_im = im.convert('RGB')
        if crop:
            rgb_im = rgb_im.crop(crop)
        rgb_im.save(pic_file_name+'.jpg', optimize=True, quality=quality)
        return pic_file_name+'.jpg'

    @staticmethod
    def ocr(pic_file_name, location=False, quality=50, crop=None):
        """
        根据包含路径的图片文件名调用API返回cor结果
        :param pic_file_name:根据包含路径的图片文件名
        :param location:是否需要识别位置信息 需要位置信息 True 表示需要
        :return:
        有位置信息
        [{'location': {'height': 59,'left': 38,'top': 827,'width': 432},
          'words': '网陈苏苏:[链接]'},
         {'location': {'height': 56,'left': 212,'top': 955,'width': 206},
          'words': '服务通知'},...]
        无位置信息
        [{'words': '微信'},
         {'words': '通讯录'},
         {'words': '发现'},
         {'words': '我'}],...
        ]
        """
        compressed_image = OCR.pre_process_img(pic_file_name,quality=quality,crop=crop)
        image = OCR.get_file_content(compressed_image)
        # 带有位置信息
        if location:
            result = client.general(image)
            # 计算words裁剪之前的真是坐标
            if crop:
                for words in result['words_result']:
                    words['location']['left'] += crop[0]
                    words['location']['top'] += crop[1]
        # 不带位置信息
        else:
            result = client.basicGeneral(image)
        if result['words_result_num'] != 0:
            return result['words_result']
        else:
            return OCR_NO_WORDS

if __name__ == '__main__':
    # result = OCR.ocr('screen.png')
    # print(result)
    result = OCR.ocr('screen.png',location=False)
    print(result)
