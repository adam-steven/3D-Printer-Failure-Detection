import cv2
import numpy as np

#OpenCV Video Retrieval
class VideoCapture:
    def __init__(self, video_source):
        #Open the video source
        self.vid = cv2.VideoCapture(video_source)

        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        #Set video source width and height
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        #Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        print(str(self.width) + "," + str(self.height))

    #Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.window.mainloop()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, frame)
            else:
                return (ret, None)
        else:
            return (ret, None)

