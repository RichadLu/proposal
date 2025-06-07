import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

def distance(p1, p2):
    return math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
def find_max_contour_area(contours):

    max_area = 0 - float('inf')
    max_c = None

    for c in contours:
        area = cv2.contourArea(c)

        if area > max_area:
            max_area = area
            max_c = c

    return [max_c]
def find_outer_corners(img, pts):

    rows, cols, _ = img.shape

    bl_dst = br_dst = tl_dst = tr_dst = float('inf')

    for p in pts:

        p = p[0]

        if distance(p, (cols*0, rows*1)) < bl_dst:
            bl_dst = distance(p, (cols*0, rows*1))
            bl = p

        if distance(p, (cols*1, rows*1)) < br_dst:
            br_dst = distance(p, (cols*1, rows*1))
            br = p

        if distance(p, (cols*0, rows*0)) < tl_dst:
            tl_dst = distance(p, (cols*0, rows*0))
            tl = p

        if distance(p, (cols*1, rows*0)) < tr_dst:
            tr_dst = distance(p, (cols*1, rows*0))
            tr = p

    pts1 = np.float32(
        [bl,  # btm left
        br,  # btm right
        tl,  # top left
        tr]  # top right
    )

    return pts1
def getcorners(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                            cv2.THRESH_BINARY_INV, 9, 3)

    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    contours = find_max_contour_area(contours) 
    img = cv2.drawContours(img, contours, -1, (0, 255, 0), 2).copy()

    c = contours[0]
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    pts = find_outer_corners(img, approx)
    return pts





