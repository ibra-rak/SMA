class Comparison :

    def __init__(self,best_criterion_name,worst_criterion_name):
        """Creates a new comparison"""
        self.best_criterion_name=best_criterion_name
        self.worst_criterion_name=worst_criterion_name

    def __str__(self):
        strdisplay=str(self.best_criterion_name)+" > "+str(self.worst_criterion_name)
        return strdisplay