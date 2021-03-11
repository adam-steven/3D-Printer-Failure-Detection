
class Obj:
    def __init__(self, location, numberOfConsecutive, numberOfMissed):
        self.loc = location
        self.cons = numberOfConsecutive
        self.miss = numberOfMissed

    def set_obj(self, location, numberOfConsecutive, numberOfMissed):
        self.loc = location
        self.cons = numberOfConsecutive
        self.miss = numberOfMissed

    def set_avr_obj(self, newlocation, newNumberOfConsecutive, newNumberOfMissed):
        x = self.loc[0] + newlocation[0]
        y = self.loc[1] + newlocation[1]
        w = self.loc[2] + newlocation[2]
        h = self.loc[3] + newlocation[3]

        self.loc = tuple([x,y,w,h])
        self.cons = self.cons + newNumberOfConsecutive
        self.miss = self.miss + newNumberOfMissed

    def get_obj(self):
        return self.loc, self.cons, self.miss

    def get_avr_obj(self):
        averagedLoc = list(int(val/self.cons) for val in self.loc)
        return averagedLoc, self.cons, self.miss



