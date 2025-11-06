from a2a.Task import Task
from a2a.Agent import Agent
import traceback

class SendMessage():
    
    def __init__(self, task:Task,agent:Agent):
        
        ''' A router which enables communication between two agents and sends instructions from 1 agent to another
        args:
            1. task : An object of type Task which contains details of the agent communication
            2. source : agent name sending the task
            3. target : agent name that will perform the task
            4. agents: a single agent object
        output:
            1. task: updated task with output
        '''

        self.task = task
        self.agent=agent
    


    def send_messages(self):

        try:
            output,artifact = self.agent.run_agent(self.task.history)
            if artifact is not None:
                self.task.task_artifact = artifact
            self.task.task_status = "success"
            self.task.task_output = output
            self.task.history.append({"role":"assistant","content":str(output)})
        except Exception as e:
            traceback.print_exc()
            self.task.task_status = "failure"
            self.task.history.append({"role":"assistant","content":"Something failed"})

        return self.task