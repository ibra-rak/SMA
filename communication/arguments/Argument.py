from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue
from preferences.Value import Value

class Argument:
    """ 
    attr :
    decision
    item
    comparison_list
    couple_values_list    
    """


    def __init__(self,boolean_decision,item):
        """creates a new arg"""
        self.decision=boolean_decision
        self.item = item
        self.comparison_list=[]
        self.couple_values_list=[] # (criterion,criterion) or (criterion,value)

    def __str__(self):
        cond="not "
        if self.decision:
                cond=""
        res = cond + self.item.__str__() + " <- "
        first = True
        for arg in self.comparison_list + self.couple_values_list:
            if first:
                first = False
            else:
                res += ", "
            res += arg.__str__()
        return res

    def argument_parsing(self):
        """ """
        avis=self.decision
        premise=self.couple_values_list
        item=self.item
        return item, avis, premise

    def add_premiss_comparison(self,criterion_name_1,criterion_name_2):
        self.comparison_list.append(Comparison(criterion_name_1,criterion_name_2)) #means criterion_name_1 > criterion_name_2
        
    def add_premiss_couple_values(self,criterion_name,value):
        self.couple_values_list.append(CoupleValue(criterion_name,value))

    def list_supporting_proposal(self,item,preferences):
        reasons=[]
        for crit in preferences.get_criterion_name_list():
            if (preferences.get_value(item,crit).value == 4) or (preferences.get_value(item,crit).value == 3):
                reasons.append(crit)
        return reasons
    
    def list_attacking_proposal(self,item,preferences):
        reasons=[]
        for crit in preferences.get_criterion_name_list():
            if (preferences.get_value(item,crit).value == 0) or (preferences.get_value(item,crit).value == 1): #correspond à very bad ou bad
                reasons.append(crit)
        return reasons
    




