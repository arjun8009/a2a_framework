import os
import joblib
import shutil

class Messages():
    '''Simple class to help correlate messages with a task id. This will help in tracking conversations across multiple tasks.'''
    def __init__(self, messages : list, task_id:str):
        self.messages = messages
        self.task_id = task_id
        self.filepath = "./message_store"
    
    def get_relevant_files(self):
        '''Function to get all relevant files corresponding to the source and target agents in the task id'''
        message_filenames = os.listdir(self.filepath)
        relevant_files = [i for i in message_filenames if (self.task_id.split("^")[0] in i) and (self.task_id.split("^")[1] in i)]
        return relevant_files
    
    def save_messages(self):
        '''Function to save messages to a filepath corresponding to this task id. Gets the old files and removes them before saving the new file'''
        files = self.get_relevant_files()
        if len(files) > 0:
            # removing old files
            for f in files:
                os.remove(os.path.join(self.filepath,f))
    
        joblib.dump(self, os.path.join(self.filepath,f"{self.task_id}.pkl"))

    def get_messages(self):
        '''Function to return all messages stored in the filepath corresponding to this task id
        outputs:
            A list of messages'''
        
        relevant_files = self.get_relevant_files()

        if len(relevant_files) == 0:
            return None
        else:
            # choosing the latest file and returning messages from that
            latest_file = sorted(relevant_files)[-1]
            loaded_messages = joblib.load(os.path.join(self.filepath,latest_file))
            return loaded_messages.messages

    def add_messages(self,messages:list=None):
        '''add explicitely new messages to the store or update existing messages. May think of what to return here later'''
            
        self.messages =  self.messages + messages
        self.save_messages()


    def add_or_update_messages(self):

        '''Function to either add new messages to the store or update existing messages. May think of what to return here later'''

        messages = self.get_messages()
        if messages is None:
            self.save_messages()
        else:
            self.messages =  messages + self.messages
            self.save_messages()