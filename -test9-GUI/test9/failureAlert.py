import cv2
import numpy as np

#OpenCV Video Retrieval
class FailAlert:
    def __init__(self, vid):
        self.vid = vid

    def alert(self, frame):
        print("PRINT FAILURE")
        cv2.imshow("Failure Img", frame)
        return


