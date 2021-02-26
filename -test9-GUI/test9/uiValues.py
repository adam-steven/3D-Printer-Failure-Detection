class UIVals:
    def __init__(self, vidWidth, vidHeight):
        self.vivid = 120
        self.certianTimeScl = 30
        self.failureRangeScl = 30 
        self.cutLeftScl = int((vidWidth/2)/2)
        self.cutRightScl = int((vidWidth/2)/2)
        self.cutBottomScl = int((vidHeight/2)/3)
        self.sensitivityScl = 400
        self.noOfModels = 1

    def set_vals(self, vivid, certianTimeScl, failureRangeScl, cutLeftScl, cutRightScl, cutBottomScl, sensitivityScl, noOfModels):
        self.vivid = int(vivid)
        self.certianTimeScl = certianTimeScl
        self.failureRangeScl = failureRangeScl 
        self.cutLeftScl = cutLeftScl 
        self.cutRightScl = cutRightScl
        self.cutBottomScl = cutBottomScl
        self.sensitivityScl = int(sensitivityScl)
        self.noOfModels = noOfModels

    def get_vals(self):
        return self.vivid, self.certianTimeScl, self.failureRangeScl, self.cutLeftScl, self.cutRightScl, self.cutBottomScl, self.sensitivityScl, self.noOfModels

