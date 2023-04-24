class CoupleValue:
    def __init__(self,criterion_name,value):
        self.criterion_name=criterion_name
        self.value=value

    def __str__(self):
        return str(self.criterion_name)+' = '+str(self.value)
    
    def get_criterion(self):
        return self.criterion_name