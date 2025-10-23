import os

# Function to set api keys. We want all api keys in one place. Useful when we want to remove them 
def set_api_keys():
    os.environ["OPENAI_API_KEY"] = "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"
    os.environ["OSNDG_API_KEY"] = "mquJppFlzV2SgEFGgrbPV1mGZeD8u33b"
    print("Openai and ngd key set successfully")
