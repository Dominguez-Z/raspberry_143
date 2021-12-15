import cv2

# 读取图片并缩放方便显示
img = cv2.imread('push_out_ready_check_cut.jpg')

# BGR转化为HSV
HSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)


# 鼠标点击响应事件
def getposHsv(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("HSV is", HSV[y, x])
        print(x,y)


def getposBgr(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Bgr is", img[y, x])
        print(x,y)


cv2.imshow("imageHSV", HSV)
cv2.imshow('image', img)
sp = img.shape
print(sp[0],sp[1])
cv2.setMouseCallback("imageHSV", getposHsv)
cv2.setMouseCallback("image", getposBgr)


cv2.waitKey(0)