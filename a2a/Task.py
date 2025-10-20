

class Task():

    def __init__(self,messages:list, task_id:str):

        ''' Single stateful conversation between agents.
        
        args:
            1. messages: A conversation history between the two agents
            2. task_id : A unique task id for the task, helps in grouping
         '''
        self.history = messages
        self.task_id = task_id
        # can be None, "success", "failure" will later add clarification
        self.task_status = None
        # agent output will later add artifacts
        self.task_output = None
        self.task_artifact = None