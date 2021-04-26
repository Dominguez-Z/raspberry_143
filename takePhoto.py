#coding=utf-8
import cv2
CV_CAP_PROP_FRAME_WIDTH = 3
CV_CAP_PROP_FRAME_HEIGHT = 4
#videoCapture.open(0)
#    videoCapture.set(CV_CAP_PROP_FRAME_WIDTH, 1920) 
#    videoCapture.set(CV_CAP_PROP_FRAME_HEIGHT, 1080) 
cap = cv2.VideoCapture(2)
cap.set(CV_CAP_PROP_FRAME_WIDTH, 640)    #set Width
cap.set(CV_CAP_PROP_FRAME_HEIGHT, 480)    #set Height
#cv2.namedWindow('medicine')

while 1:
    ret, frame = cap.read()
#    r, g, b = cv2.split(frame)    #拆分
    cv2.imshow('medicine', frame)
#    cv2.imshow('B', b)
    k = cv2.waitKey(1) & 0xFF 
    if k == ord('t'):
        file_name = input('输入文件名>>>')
        file_path = '/home/pi/kaibo/'+ file_name + '.jpg'
        cv2.imwrite(file_path, frame)
        print('ok')
    elif k == ord('q'):    #press 'q' to quit
        break
#when everthing done, release the capture     
cap.release()
cv2.destroyAllWindows()