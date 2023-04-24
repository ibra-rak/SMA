from mesa import Model
from mesa.time import RandomActivation
import pandas as pd
import random


from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.mailbox.Mailbox import Mailbox
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService

from preferences.Preferences import Preferences
from communication.preferences.CriterionName import CriterionName
from communication.preferences.CriterionValue import CriterionValue
from communication.preferences.Item import Item
from communication.preferences.Value import Value

from communication.arguments.Argument import Argument

class ArgumentAgent(CommunicatingAgent):
    """ ArgumentAgent which inherit from CommunicatingAgent ."""

    def __init__ ( self , unique_id , model , name , preferences ) :
        super().__init__( unique_id , model , name)
        self.preference = preferences

    def step(self):
        super().step()
        

    def get_preference(self):
        return self.preference

    def generate_preferences(self,list_items,list_criterions=[CriterionName.NOISE,CriterionName.PRODUCTION_COST, CriterionName.DURABILITY, CriterionName.ENVIRONMENT_IMPACT, CriterionName.CONSUMPTION]):
        """ 
        Set the preferences of the agent 
        list_criterion = [CriterionName.NOISE,CriterionName.PRODUCTION_COST, CriterionName.DURABILITY, CriterionName.ENVIRONMENT_IMPACT, CriterionName.CONSUMPTION] for instance
        """
        self.preference.set_criterion_name_list(list_criterions)
        for x in list_items.keys():
            for crit in list_items[x].keys():
                self.preference.add_criterion_value(CriterionValue(x,crit,list_items[x][crit]))

    def support_proposal(self,item):
        """ """
        argument=Argument(True,item)
        reasons=argument.list_supporting_proposal(item,self.get_preference())
        if len(reasons)>0:
            best_crit=reasons[0] #since they are sorted by preference of the agent, that his best argument
            argument.add_premiss_couple_values(best_crit,self.preference.get_value(item,best_crit))
            return argument
     
        else:
            return None
        
    def attack_proposal(self,item,proposal):
        argument=Argument(False,item)
        constructed=False
        _, _ , premise = proposal.argument_parsing()
        critere=premise[0].get_criterion()

        #cas critere nul chez nous
        valeur_crit=self.preference.get_value(item,critere).value
        if valeur_crit<2:
            argument.add_premiss_couple_values(critere,self.preference.get_value(item,critere))
            return argument
        
        #cas critere plus important est mauvais
        liste_critere=self.preference.get_criterion_name_list()
        for k in range(len(liste_critere)):
            if liste_critere[k]==critere:
                index=k


        for x in range(index):
            test=self.preference.get_value(item,liste_critere[x]).value
            if test<2:
                argument.add_premiss_couple_values(liste_critere[x],self.preference.get_value(item,liste_critere[x]))
                argument.add_premiss_comparison(liste_critere[x],critere)
                return argument

        if not constructed:
            return None





class ArgumentModel(Model):
    def __init__(self):
        self.schedule=RandomActivation(self)
        self.__messages_service=MessageService(self.schedule)

        agent_1 = ArgumentAgent(1, self, "A1" , Preferences())
        agent_2 = ArgumentAgent(2, self, "A2" , Preferences())

        self.schedule.add(agent_1)
        self.schedule.add(agent_2)

        self.running=True


    def step(self): 
        self.__messages_service.dispatch_messages() 
        self.schedule.step()

        

if __name__ == "__main__": 
    argument_model = ArgumentModel()

    agent0 = argument_model.schedule.agents[0]
    agent1 = argument_model.schedule.agents[1]

    list_item=[]
    list_items1={}
    list_items2={}

    voitures=pd.read_csv("./templateSMA.csv")

    pvalues=[Value.VERY_BAD,Value.BAD,Value.AVERAGE,Value.GOOD,Value.VERY_GOOD]
    critere_dict={"Cout_prod":CriterionName.PRODUCTION_COST,"Consumption":CriterionName.CONSUMPTION,"Durability":CriterionName.DURABILITY,"Noise":CriterionName.NOISE,"Environnement":CriterionName.ENVIRONMENT_IMPACT}

    for index, row in voitures.iterrows():
        item=Item(row["Car name"],row["Description"])
        list_item.append(item)
        dict_item1={}
        dict_item2={}
        for x in critere_dict.keys():
            dict_item1[critere_dict[x]]=pvalues[row[str(x)+"1"]]
            dict_item2[critere_dict[x]]=pvalues[row[str(x)+"2"]]
        list_items1[item]=dict_item1
        list_items2[item]=dict_item2

    
    agent0.generate_preferences(list_items1)
    agent1.generate_preferences(list_items2,[CriterionName.PRODUCTION_COST, CriterionName.DURABILITY,CriterionName.NOISE, CriterionName.ENVIRONMENT_IMPACT, CriterionName.CONSUMPTION])


    dispute=True
    first_message=Message(agent0.get_name(), agent1.get_name(), MessagePerformative.PROPOSE, agent0.get_preference().most_preferred(list_item) )
    agent0.send_message(first_message)
    turn=0

    mode=True #on aboutit forcément à un accord ? True si les agents font des concessions (ne considèrent plus dans leur calcul de top choix les items deja eliminés)

    items_not_concerned=list_item.copy()

    while dispute:

        if turn%2==0:
            agent_to_answer=agent1
            agent_to_send=agent0
        else:
            agent_to_answer=agent0
            agent_to_send=agent1

        turn+=1

        mess=agent_to_answer.get_new_messages()[0]
        performative=mess.get_performative()
        if type(mess.get_content())==type(Argument(True,"")):
            item,decision,premise=mess.get_content().argument_parsing()
            argument=mess.get_content()
        elif type(mess.get_content())==type(Item("","")):
            item=mess.get_content()
            argument=None
        
        if mode:
                    comparative=items_not_concerned.copy()
        else:
                    comparative=list_item

        if performative==MessagePerformative.PROPOSE:
            if agent_to_answer.preference.is_item_among_top_10_percent(item,comparative) : #si il est dans son top : accepte
                dispute=False
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.ACCEPT, item))
            else: #sinon, pourquoi ?
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.ASK_WHY, item))

        elif performative==MessagePerformative.ASK_WHY: #il doit argumenter
            argu=agent_to_answer.support_proposal(item)
            if argu==None:
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.PROPOSE, agent_to_answer.get_preference().most_preferred(comparative)))
            else:
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.ARGUE, argu))

        elif performative==MessagePerformative.ARGUE : #si il recoit un argue à propos d'un nouveau élément (non évoqué précédemment)
            sender_opinion=decision
            if sender_opinion and agent_to_answer.preference.is_item_among_top_10_percent(item,comparative+[item]) : # si il est dans son top, c'est bon 
                dispute=False
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.ACCEPT, item))
            elif not sender_opinion and not agent_to_answer.preference.is_item_among_top_10_percent(item,comparative+[item]):
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.PROPOSE, agent_to_answer.get_preference().most_preferred(comparative)))
            elif not sender_opinion and agent_to_answer.preference.is_item_among_top_10_percent(item,comparative+[item]):
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.PROPOSE, agent_to_answer.get_preference().most_preferred(comparative)))
            else:
                arg=agent_to_answer.attack_proposal(item,argument)
                if arg==None:
                    arg=agent_to_answer.support_proposal(agent_to_answer.get_preference().most_preferred(comparative))
                agent_to_answer.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.ARGUE, arg))

        if item in items_not_concerned:
            items_not_concerned.remove(item)

    agent_to_send.send_message(Message(agent_to_answer.get_name(), agent_to_send.get_name(), MessagePerformative.COMMIT, item))
    agent_to_answer.send_message(Message(agent_to_send.get_name(), agent_to_answer.get_name(), MessagePerformative.COMMIT, item))

    argument_model.step()
