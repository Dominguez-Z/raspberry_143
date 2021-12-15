import qrcode
from PIL import Image
import os
from PIL import ImageDraw
from PIL import ImageFont


# 生成二维码图片
def make_qr(str, save):
    qr = qrcode.QRCode(
        version=1,  # 生成二维码尺寸的大小 1-40  1:21*21（21+(n-1)*4）
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # L:7% M:15% Q:25% H:30%
        box_size=10,  # 每个格子的像素大小
        border=1,  # 边框的格子宽度大小
    )
    qr.add_data(str)
    qr.make(fit=True)
    img = qr.make_image()

    # # 加中间logo图片
    # icon = Image.open("logo.png")
    # img_w, img_h = img.size
    # factor = 4
    # size_w = int(img_w / factor)
    # size_h = int(img_h / factor)
    # icon_w, icon_h = icon.size
    # if icon_w > size_w:
    #     icon_w = size_w
    # if icon_h > size_h:
    #     icon_h = size_h
    # icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
    # w = int((img_w - icon_w) / 2)
    # h = int((img_h - icon_h) / 2)
    # img.paste(icon, (w, h), icon)
    # #print(str)

    img.save(save)

def info(name,code,name1):
    make_qr(code, name)
    oriImg = Image.open("底图.png")
    oriImg2 = Image.open(name)
    oriImg2 = oriImg2.resize((285, 290))#设置二维码大小
    oriImg.paste(oriImg2, (100, 95))#将二维码放在底图上
    draw = ImageDraw.Draw(oriImg)
    font = ImageFont.truetype("simsun.ttc", 40)#设置字体
    draw.text((100, 375), "编号"+code, (50, 50, 51), font=font)#把字添加到图片上
    oriImg.save(name1)


def creat_back():
    # 创建新图，RGB模式，230*230，全白
    img = Image.new('RGB', (230, 230+80), (255, 255, 255))
    # img.show()
    img.save("background.jpg")


def add_info(name,name1):
    oriImg = Image.open("background.jpg")
    oriImg2 = Image.open(name)
    # oriImg2 = oriImg2.resize((285, 290))#设置二维码大小
    oriImg.paste(oriImg2, (0, 0))#将二维码放在底图上

    # 添加文字
    draw = ImageDraw.Draw(oriImg)
    font = ImageFont.truetype("simhei.ttf", 30)#设置字体，黑体
    draw.text((20, 230), "编号", (1, 1, 1), font=font)#把字添加到图片上
    draw.text((20, 270), code, (1, 1, 1), font=font)
    oriImg.save(name1)


code=9999999999
code=str(code)
print(code)
name= code+"_1.jpg"
print(name)
name1='编号'+code+"_1.jpg"
make_qr(code,name)
# info(name,code,name1)
# creat_back()
# add_info(name,name1)
