#!/usr/bin/env python

import os
import sys
import cv2
from math import floor
g_event_status = {'event': None}
g_images = {}
g_rendered_images = {}

def computeRatio(p, q):
    rp = (float(p[0]) / g_images[g_event_status['focus_window']].shape[:2][1],
          float(p[1]) / g_images[g_event_status['focus_window']].shape[:2][0])
    rq = (float(q[0]) / g_images[g_event_status['focus_window']].shape[:2][1],
          float(q[1]) / g_images[g_event_status['focus_window']].shape[:2][0])
    return (rp, rq)

def computePoint(img, rp, rq):
    P = (int(rp[0] * img.shape[:2][1]),
         int(rp[1] * img.shape[:2][0]))
    Q = (int(rq[0] * img.shape[:2][1]),
         int(rq[1] * img.shape[:2][0]))
    return (P, Q)

def drawRegions():
    global g_event_status, g_images
    if (g_event_status['event'] != 'clicked' and
        g_event_status['event'] != 'done'):
        for f, img in g_images.items():
            cv2.imshow(f, img)
        return
    p = g_event_status['down_pos']
    q = g_event_status['up_pos']
    (rp, rq) = computeRatio(p, q)
    # compute ratio
    for f, img in g_images.items():
        (P, Q) = computePoint(img, rp, rq)
        g_rendered_images[f] = g_images[f].copy()
        cv2.rectangle(g_rendered_images[f], P, Q, (0,0,255))
        cv2.imshow(f, g_rendered_images[f])

def saveImages():
    p = g_event_status['down_pos']
    q = g_event_status['up_pos']
    (rp, rq) = computeRatio(p, q)
    for f, img in g_images.items():
        (P, Q) = computePoint(img, rp, rq)
        min_x = min(P[0], Q[0])
        max_x = max(P[0], Q[0])
        min_y = min(P[1], Q[1])
        max_y = max(P[1], Q[1])
        cropped = img[min_y:(max_y - min_y), min_x:(max_x - min_x)]
        (filename, suffix) = os.path.basename(f).split(".")
        outname = filename + "_cropped." + suffix
        print "saving image", outname
        cv2.imwrite(os.path.join(os.path.dirname(f), outname), cropped)
        
def mouseCallbackFunction(name):
    return lambda event,x,y,flags,param: mouseCallback(event, x, y, flags, param, name)

def mouseCallback(event, x, y, flags, param, name):
    global g_event_status
    if event == cv2.EVENT_LBUTTONDOWN:
        g_event_status['event'] = 'clicked'
        g_event_status['focus_window'] = name
        g_event_status['down_pos'] = (x, y)
        g_event_status['up_pos'] = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE:
        if (g_event_status['event'] == 'clicked' and
            g_event_status['focus_window'] == name):
            g_event_status['up_pos'] = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        if (g_event_status['event'] == 'clicked' and
            g_event_status['focus_window'] == name):
            g_event_status['up_pos'] = (x, y)
            g_event_status['event'] = 'done'
        else:
            g_event_status['event'] = None
    drawRegions()
    
for f in sys.argv[1:]:
    cv2.namedWindow(f, cv2.CV_WINDOW_AUTOSIZE)
    cv2.setMouseCallback(f, mouseCallbackFunction(f))

for f in sys.argv[1:]:
    g_images[f] = cv2.imread(f)
    g_rendered_images[f] = g_images[f].copy()

[cv2.imshow(f, img) for f, img in g_images.items()]

print "Press ENTER to save cropped image"

while True:
    key = cv2.waitKey(10)
    if key == ord("\n"):               # Enter
        saveImages()
        sys.exit(0)
    elif key == ord("q") or key == ord("Q"):
        sys.exit(1)             # quit
        
