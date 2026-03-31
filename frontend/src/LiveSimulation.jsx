import React, { useState } from 'react';
import { Box, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import AgentGraphLive from "./AgentGraphLive";
import ChatbotCard from "./ChatbotCard";
import CodeAgentPanel from './CodeAgentPanel';

export default function LiveSimulation(){

    const [choice, setChoice] = useState('');

    const sendConfig = async(selectedChoice) =>{

        try{
            const url = "http://localhost:5000/config-choice"
            const response = await fetch(url,{
                method:'POST',
                headers: {
                'Content-Type': 'application/json',
                },
                body:JSON.stringify({'choice':selectedChoice})
            })

            if(response.ok){
                console.log("Set successfully")
            }else{
                console.log("Set unsuccessfully")
            }
        }catch{
            console.log("ERROR IN CHOICE")
        }
    }

    const handleChange = (event) => {
    const selectedValue = event.target.value;
    setChoice(selectedValue);
    sendConfig(selectedValue);
    };

    return(

        <Box sx={{
            display:"flex",
            flexDirection:"column",
            height: "100vh",
            width: "100vw",
            overflow: "hidden",
            backgroundColor: 'white',
            gap: 0,
        }}>

            <Box sx={{
                flexShrink: 0,
                p:2,
                zIndex:1000
            }}>
                <FormControl fullWidth size="small">
                    <InputLabel id="config-choice-label">Select Configuration</InputLabel>
                    <Select
                    labelId="config-choice-label"
                    id="config-choice-select"
                    value={choice}
                    label="Select Configuration"
                    onChange={handleChange}
                    >   
                    <MenuItem value="agent_config_with_human_confirmation">Agent Config With Human Confirmation</MenuItem>

                    </Select>
            </FormControl>

            </Box>

            <Box
                sx={{
                display:"flex",
                flex:1,
                flexDirection:"row",
                minHeight: 0,
                overflow: "hidden",
                gap: 0,
                }}
            >
                <Box
                sx={{
                flex: 1,
                height: "100%",
                overflow: "hidden",
                borderRight: "1px solid",
                borderColor: "divider",
                }}
            >
                <ChatbotCard />
            </Box>

            {/* Right Panel - AgentGraphLive */}
           <Box sx={{ flex: 1, height: "100%", display: "flex", flexDirection: "column", overflow: "hidden" }}>
 
                    {/* Top-right — Agent graph */}
                    <Box sx={{ flex: 1, minHeight: 0, overflow: "auto", borderBottom: "1px solid", borderColor: "divider" }}>
                        <AgentGraphLive />
                    </Box>
 
                    {/* Bottom-right — DB call panel */}
                    <Box sx={{ flex: 1, minHeight: 0, overflow: "hidden", display: "flex", flexDirection:"column"}}>
                        <CodeAgentPanel />
                    </Box>
 
 
            </Box> 
            
            </Box>
            
        </Box>
    );
}