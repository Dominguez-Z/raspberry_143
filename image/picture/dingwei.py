import cv2
import numpy as np

def findpos(img1, thre):
    grimg1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    segline = grimg1[:, 1550] > thre  # can change 1550 to other positions
    allpos1 = np.where(segline[:-2] & (~segline[2:]) == True)[0]

    pos1 = allpos1[0]
    if pos1 < 270:  # can be adjusted
        pos1 = allpos1[1]

    allpos3 = np.where(~segline[:-2] & (segline[2:]) == True)[0]
    pos3 = allpos3[2]
    if pos3 < 600:
        pos3 = allpos3[3]
    #print(i,pos1,pos3)
    print(pos1, pos3)

    return pos1, pos3, allpos1, allpos3  #x 1550, y pos1, pos2

def main():
    video0_img = cv2.imread("R_0.00_1.jpg")
    cv2.namedWindow("picture", cv2.WINDOW_NORMAL)
    cv2.imshow("picture", video0_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

main()
