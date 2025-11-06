from a2a.AgentCard import AgentCard


''' Here we will store the AgentCard templates for all out OS agents. So we do not need to copy paste again and again'''

address_agent_card = AgentCard(agent_name="address",
                               agent_description="a search agent for ordance surveys address database, Given a query you will try to find relevant addresses or places given a name of a place or address",
                               capabilities=["1. Given a place name or address name it will search it",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. It cannot apply conditions. That job is for the plotting agent"],
                                input_modes=["query : string"],
                                output_modes=["output and the artifact name"])


building_agent_card = AgentCard(agent_name="buildings",
                               agent_description="a search agent for ordance surveys buildings database, Given a query you will try to find relevant buildings",
                               capabilities=["1. Given a query it will search it. Best used when the query is generic and asks for types or classes of buildings or specific building properties like rooms, floors, roof types etc",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. However this search is more generic as it searches using types or filters and not names. Still try to ask it and it will try to answer"],
                                input_modes=["query : string"],
                                output_modes=["output and the artifact name"])


named_area_agent_card = AgentCard(agent_name="named_area",
                                  agent_description="a search agent for ordance surveys named area database. A named area by OS is defined as : A settlement, locality, geographical feature, or area of water that has a name, represented as a polygon. It contains information related to cities, counties, geographical descriptions etc ",
                                  capabilities=["1. Given a named area like a city or a place it will search it",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. It cannot apply conditions. That job is for the plotting agent"],
                                    input_modes=["query : string"],
                                    output_modes=["output and the artifact name"])

plotting_agent_card = AgentCard(agent_name="plotting_agent",
                                agent_description="A plotting agent that given artifact names, spatial conditions of query can plot them",
                                capabilities=["Given names of aritfacts and spatial conditions can plot them"],
                                input_modes=["query : str containing what to plot and spatial conditions"],
                                output_modes=["string containing generated summary output and artifact name containing the map"])


coding_agent_details = AgentCard(agent_name="data_analysis_agent",
                                    agent_description="It is a useful agent that can perform data analysis on a given data set and provide insights",
                                    capabilities=["Given a dataset, it can perform various data analysis tasks like summarization, statistical analysis, visualization etc."],
                                    input_modes=["task in str with the filenames provided to analyse data"],
                                    output_modes=["str","list out outputs including summaries, artifacts like plots and data files and their name and description"])
