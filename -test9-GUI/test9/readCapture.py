import cv2
from constants import FRAME_WIDTH, FRAME_HEIGHT

#OpenCV Video Retrieval
class VideoCapture:
    def __init__(self, video_source):
        #Open the video source
        self.vid = cv2.VideoCapture(video_source)

        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        #Set video source width and height
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        #Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        print(str(self.width) + "," + str(self.height))

    #Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.window.mainloop()

    #Read the video source information 
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, frame)

        return (False, None)

