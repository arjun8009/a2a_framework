import React, { useState } from 'react';
import { Box, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import AgentGraphLive from "./AgentGraphLive";
import ChatbotCard from "./ChatbotCard";

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
                    <MenuItem value="agent_config_with_human">Agent Config With Human</MenuItem>
                    <MenuItem value="agent_config">Agent Config</MenuItem>
                    <MenuItem value="agent_config_with_human_updated">Agent Config With Human Updated</MenuItem>
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
            <Box
                sx={{
                flex: 1,
                height: "100%",
                overflow: "auto",
                }}
            >
                <AgentGraphLive />
            </Box>
            </Box>
            
        </Box>
    );
}