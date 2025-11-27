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
