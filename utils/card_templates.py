from a2a.AgentCard import AgentCard


''' Here we will store the AgentCard templates for all out OS agents. So we do not need to copy paste again and again'''


host_agent_card = AgentCard(agent_name="host_agent",
                            agent_description="A geospatial helper agent",
                            capabilities=["solve user geospatial queries"],
                            input_modes=["query:string"],
                            output_modes=["output:string"])

address_agent_card = AgentCard(agent_name="address",
                               agent_description="a search agent for ordance surveys address database within an area, Given a query you will try to find relevant addresses or places given a name of a place or address. Artifacts are points",
                               capabilities=["1. Given a place name or address name and the artifact name of where to search, it will search places in an area",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. It cannot apply conditions. That job is for the plotting agent",
                                             "6. Artifacts contain points of addresses"],
                                input_modes=["query : string "],
                                output_modes=["output and the artifact name"])


building_agent_card = AgentCard(agent_name="buildings",
                               agent_description="a search agent for ordance surveys buildings database within an area, Given a query you will try to find relevant buildings, Artifacts are small building polygons",
                               capabilities=["1. Given a query it will search it in an area artifact. Best used when the query asks for various types or classes of buildings",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. Artifacts contain polygons of buildings"],
                                input_modes=["query : string"],
                                output_modes=["output and the artifact name"])


named_area_agent_card = AgentCard(agent_name="named_area",
                                  agent_description="a search agent for ordance surveys named area database. A named area by OS is defined as : A settlement, locality, geographical feature, or area of water that has a name, represented as a polygon. It contains information related to cities, counties, geographical descriptions etc. Artifacts are area polygons ",
                                  capabilities=["1. Given a named area like a city or a place it will search it",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. It cannot apply conditions. That job is for the plotting agent",
                                             "6. Artifacts contain polygons of areas"],
                                    input_modes=["query : string"],
                                    output_modes=["output and the artifact name"])

plotting_agent_card = AgentCard(agent_name="plotting_agent",
                                agent_description="A plotting agent that given artifact names, spatial conditions of query can plot them",
                                capabilities=["Given names of aritfacts and spatial conditions can plot them"],
                                input_modes=["query : str containing what to plot and spatial conditions"],
                                output_modes=["string containing generated summary output and artifact name containing the map"])


coding_agent_details = AgentCard(agent_name="data_analysis_agent",
                                    agent_description="It is a useful agent that can perform data analysis on a given data set and provide insights",
                                    capabilities=["Given a dataset, it can perform various data analysis tasks like summarization, statistical analysis, visualization etc."
                                                  "Cannot search for point in 1 artifact using another."],
                                    input_modes=["task in str with the filenames provided to analyse data"],
                                    output_modes=["str","list out outputs including summaries, artifacts like plots and data files and their name and description"])
