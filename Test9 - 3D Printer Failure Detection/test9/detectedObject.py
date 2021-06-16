#A potectial or definite object found in the camera feed (automaticDetection.py 1 <- M detectedObject.py)
class Obj:
    def __init__(self, location, numberOfConsecutive, numberOfMissed):
        self.loc = location
        self.cons = numberOfConsecutive
        self.miss = numberOfMissed
    
    def set_obj(self, location, numberOfConsecutive, numberOfMissed):
        self.loc = location
        self.cons = numberOfConsecutive
        self.miss = numberOfMissed

    #Adds a new found contour's values to this object's values
    def set_avr_obj(self, newlocation, newNumberOfConsecutive, newNumberOfMissed):
        x = self.loc[0] + newlocation[0]
        y = self.loc[1] + newlocation[1]
        w = self.loc[2] + newlocation[2]
        h = self.loc[3] + newlocation[3]

        self.loc = tuple([x,y,w,h])
        self.cons = self.cons + newNumberOfConsecutive

        if self.miss + newNumberOfMissed >= 0:
            self.miss = self.miss + newNumberOfMissed

    #Sets misses to 0 (for definite objects) 
    def reset_obj_misses(self):
        self.miss = 0

    def get_obj(self):
        return self.loc, self.cons, self.miss

    #Calculates the objects postion on the camera feed before sending 
    def get_avr_obj(self):
        averagedLoc = list(int(val/self.cons) for val in self.loc)
        return averagedLoc, self.cons, self.miss




