from utils.keys import set_api_keys
from openai import OpenAI
from pydantic import BaseModel,Field
set_api_keys()

client = OpenAI()
class Explain(BaseModel):
    columns : list[list[str]] = Field(description="All columns used for filtering for each database as a list of list ")
    conditions : list[list[str]] = Field(description="Corresponding conditions imposed on the columns for each database")
    plotting : bool = Field(description="True is the code is plotting anything on a map else False")

prompt = """You are a code explainer. You will be given a peice of code and the database name you will output the columns used by the code to filter the dataset and the \
    conditions imposed on the column like searches, thresholds or filtering using categories for that database. List them out correctly
    example : INPUT : code : <CODE> and databases : [D1, D2]. so output should be columns = [[c11,c12], [c21,c22]] conditions = [[cd11,cd12],[cd21,cd22]] \
    where c11 and c12 are columns used by the code for database 1 and c21 and c22 are columns used by the code for database 2 and same for conditions. \
    Finally plotting is True if the code is plotting something on a map else False
    """

def explain_code(code):

    messages = [{"role":"system", "content":prompt},
                {"role":"user","content":code}]

    # use the OpenAI responses API with a pydantic schema to enforce structured output
    # we choose a reliable model that supports the newer beta chat completions parse endpoint
    response = client.beta.chat.completions.parse(
        model="gpt-4.1",
        temperature=0,
        messages=messages,
        response_format=Explain,
    )

    # the parser returns choices where message.parsed adheres to the Explain schema
    parsed = response.choices[0].message.parsed
    # return as native python types (list of strings)
    return parsed.columns,parsed.conditions,parsed.plotting
