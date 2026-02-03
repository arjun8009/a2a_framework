from a2a.AgentCard import AgentCard


''' Here we will store the AgentCard templates for all out OS agents. So we do not need to copy paste again and again'''


host_agent_card = AgentCard(agent_name="host_agent",
                            agent_description="A geospatial helper agent",
                            capabilities=["solve user geospatial queries"],
                            input_modes=["query:string"],
                            output_modes=["output:string"])

planning_agent_card = AgentCard(agent_name="planning_agent",
                            agent_description="A geospatial planning agent",
                            capabilities=["Provides a sequence of steps to solve the queries"],
                            input_modes=["query:string"],
                            output_modes=["output:string"])


address_agent_card = AgentCard(agent_name="address",
                               agent_description="a search agent for ordance surveys address database within an area, Given a query you will try to find relevant addresses or places given a name of a place or address.Use this only for named location geolocation. Artifacts are points",
                               capabilities=["1. Given a place name or address name and the artifact name of where to search, it will search places in an area",
                                             "2. Note : only use this for named entitiy geo coding only. Do not using it for finding generic things without names"
                                             "3. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "4. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "5. Has access to coding agent so can search further if you ask it to",
                                             "6. It cannot apply conditions. That job is for the plotting agent",
                                             "7. Artifacts contain points of addresses"],
                                input_modes=["query : string "],
                                output_modes=["output and the artifact name"])


building_agent_card = AgentCard(agent_name="buildings",
                               agent_description="a search agent for ordance surveys buildings database within an area, Given a query you will try to find relevant buildings.It has 89 features and is a rich set so normally it can filter for all conditions related to buildings.Artifacts are small building polygons",
                               capabilities=["1. Given a query it will search it in an area artifact. It is very rich with 89 features so all conditions attached to buildings can be handled by it.",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. Artifacts contain polygons of buildings"],
                                input_modes=["query : string"],
                                output_modes=["output and the artifact name"])


water_features_agent_card = AgentCard(agent_name="water_features",
                               agent_description="a search agent for ordance surveys water features database within an area, Given a query you will try to find relevant features such as watercourses, lakes, drains, springs and intertidal watercourses across Great Britain",
                               capabilities=["1. Given a query it will search it in an area artifact.",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. Artifacts contain points and polygons of water features"],
                                input_modes=["query : string"],
                                output_modes=["output and the artifact name"])


water_network_agent_card = AgentCard(agent_name="water_network",
                               agent_description="a search agent for ordance surveys water network database within an area, Given a query you will try to find relevant Rivers, streams, lakes, lochs, drains and canals ",
                               capabilities=["1. Given a query it will search it in an area artifact.",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. Artifacts contain lines of Rivers, streams, lakes"],
                                input_modes=["query : string"],
                                output_modes=["output and the artifact name"])

land_features_agent_card = AgentCard(agent_name="land_features",
                               agent_description="a search agent for ordance surveys land features database within an area, Given a query, it will try to find relevant features which can be manmade \
                                                (for example, tennis courts, residential gardens, construction sites) or natural land \
                                                (for example, coniferous trees, cliffs, heath or rough grassland), but excludes features exclusively associated with buildings, structures, transport and water.",
                                capabilities=["1. Given a query it will search it in an area artifact.",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. Artifacts contain point, line and polygon features of land features"],
                                input_modes=["query : string"],
                                output_modes=["output and the artifact name"])

land_use_features_agent_card = AgentCard(agent_name="land_use_features",
                               agent_description="a search agent for ordance surveys land use features database within an area, Given a query, it will try to find relevant features which are geographical representations \
                                of areas identified as having a specific purpose (such as schools, universities, and caravan parks), as well as information about access to such areas. \
                                Polygon feature which represents the recognisable extent of certain types of function or activity. Examples include a caravan site, a university, and a railway centre.",
                                capabilities=["1. Given a query it will search it in an area artifact.",
                                             "2. If you need to search within an area bbox then you need to tell it the name of the artifact containing the bbox",
                                             "3. If you give it the name of the artifact bbox and ask it to search within it, it will do so",
                                             "4. Has access to coding agent so can search further if you ask it to",
                                             "5. Artifacts contain point, line and polygon features of land features"],
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

structure_agent_card = AgentCard(agent_name="structures_agent",
                                agent_description="a search agent for ordance surveys structure database within an area, Polygon feature representing a manmade construction that is not a building. Examples include a mast, a chimney, crane, solar panel etc, Artifacts are structure polygons",
                                capabilities=["1. Given a structure type or description it will search it in an area artifact",
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
                                    capabilities=["Given a dataset, it can perform various data analysis tasks like summarization, statistical analysis, visualization etc."
                                                  "Cannot search for point in 1 artifact using another."],
                                    input_modes=["task in str with the filenames provided to analyse data"],
                                    output_modes=["str","list out outputs including summaries, artifacts like plots and data files and their name and description"])

human_agent_card = AgentCard(agent_name="human_agent",
                                agent_description="A human agent that can be queried for help when there is ambiguity in the user query",
                                capabilities=["Can help resolve ambiguities in user queries",
                                            "Can provide clarifications on spatial conditions"],
                                input_modes=["query : str containing the ambiguity or clarification needed"],
                                output_modes=["string containing the human response"])