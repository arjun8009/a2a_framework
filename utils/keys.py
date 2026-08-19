import os

# Function to set api keys. We want all api keys in one place. Useful when we want to remove them 
def set_api_keys():
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["OSNDG_API_KEY"] = ""
    print("Openai and ngd key set successfully")
