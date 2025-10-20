from Task import Task
from Agent import Agent

class SendMessage():
    
    def __init__(self, task:Task, source:str, target:str, agents:list[Agent]):
        
        ''' A router which enables communication between two agents and sends instructions from 1 agent to another
        args:
            1. task : An object of type Task which contains details of the agent communication
            2. source : agent name sending the task
            3. target : agent name that will perform the task
            4. agents: a list of agent objects
        output:
            1. task: updated task with output
        '''

        self.task = task
        self.source = source
        self.target = target
        self.agents=agents

        return self.send_messages()

    def send_messages(self):

        agent_names = [i.agent_identity.agent_name for i in self.agents]
        target_agent = self.agents[agent_names.index(self.target)]

        try:
            output = target_agent.run_agent(self.task.history)
            self.task.task_status = "success"
            self.task.task_output = output
        except Exception as e:
            self.task.task_status = "failure"

        return self.task