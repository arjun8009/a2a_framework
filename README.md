## OS Project Phase 2

* utils : directory containing files related to LLM implementation, tools and defaults usable prompts
* a2a : Files related to agents, artifacts, send message functionality
* system_test.ipynb : utility notebook to test every line of code we write and every script we make. Usage of llms.py, agents and multi-agents demonstrated here.
* Requirements.txt is the dependency file
* You will need ollama to run opensource llms. Download here : https://ollama.com/
* install llama3.2 to test the examples
* frontend: files related to simulation visualisation
* visualization : files related to backend functionality of the visualization
* agent_frameworks : config files that can make agents of different functionality

#### Making New agent frameworks
* The process is simple. Use the templates in agent_frameworks folder
* If using some new agent then add the agent details in the config files and if using new variables like prompts, tools etc then add the mapping in utils.registry

#### commands to run simulation UI

```bash
    cd frontend
    npm start
```

#### Commands to run backend
```bash
    cd visualization
    python server.py
```
#### Running from the backend only as an API

```python
import pandas as pd
import json
from utils.initialize_os_agents import OSAgentsInitializer
from utils.keys import set_api_keys
from utils.tools import human_send_message
set_api_keys()
import shutil
import joblib
import os

config = None
with open(r"agent_frameworks\agent_config_with_human_confirmation.json","rb") as file:
    config = json.load(file)

# Now that things are initialised
agent_archiecture = OSAgentsInitializer(config,"log",diff_dir=None).initialize_all_agents()

human_send_message(message="Find all buildings in Exeter that are more than 10m in height. Return the final artifact with the data and a plot",target_agent=[agent_archiecture["host_agent"]])
```

#### Delete memory after a few conversations using 
```python
shutil.rmtree("artifacts")
shutil.rmtree("message_store")
os.makedirs("artifacts", exist_ok=True)
os.makedirs("message_store", exist_ok=True)
```
while it has long memory. Queries can take lots of context due to the processing required. Hence it is good to delete memory after 3-5 queries




