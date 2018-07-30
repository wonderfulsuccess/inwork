# 该文件旨在让本机OCR的效果更好
import pytesseract
from PIL import Image


image = Image.open('screen_cap.png')
boxes = pytesseract.image_to_string(image, lang='chi_sim')
print(boxes)


