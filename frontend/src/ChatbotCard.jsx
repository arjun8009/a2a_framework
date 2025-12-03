import React, { useState } from "react";
import ChatUI from "./ChatInterface"
import {
  Box,
  Card,
  CardHeader,
  TextField,
  Button,
  Typography,
  Link,
  Avatar,
  Grid,
  Paper,
  Select
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ArtifactWindow from "./ArtifactWindow";

export default function ChatbotCard() {

  const [open,setOpen] = useState(false)
  const [data,setData] = useState([])

  const getArtifacts = async() =>{
    const url = "http://localhost:5000/get-artifacts"
    try{
      const response = await fetch(url,{
        method:"POST",
        headers: {
            'Content-Type': 'application/json',
            },
      });
      if(response.ok){
        const result = await response.json()
        setData(result)
      }else{
        setData([])
      }
    }catch(error){
      setData([])
    }
  }

  const handleOpen = ()=>{
    getArtifacts()
    setOpen(true)
  }

  const handleClose = () =>{
    setOpen(false)
  }

  return (
    <>
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden"
      }}
    >
      {/* Header */}
      <CardHeader
        title={<h2>Ordnance Survey Geospatial Chatbot</h2>}
        sx={{
          background: "#334195",
          color: "white",
          display: "flex",
          flexDirection: { xs: "column", sm: "row" },
          alignItems: { xs: "flex-start", sm: "center" }
        }}
        avatar={[
          <img
            src="https://th.bing.com/th/id/OIP.hyEHEn1JS9ewOosdS1NzoQAAAA"
            style={{ width: "70px", height: "50px" }}
          />
        ]}
        action = {
          <Button
          variant="outlined"
          sx={{ color: "white", fontSize: { xs: "10px", sm: "12px", md: "14px" } }}
          onClick={handleOpen}
          >
            Aritfacts
          </Button>
        }
      />

      {/* Chat UI must grow */}
      <Box
        sx={{
          flex: 1,
          minHeight: 0,        // VERY IMPORTANT
          overflow: "hidden",  // ChatUI will handle inner scrolling
        }}
      >
        <ChatUI />
      </Box>

      {/* Footer */}
      <Typography fontSize={"12px"} sx={{ textAlign: "center", p: 1 }}>
        The content produced by the chatbot is AI-generated and may not always be accurate. Whilst we strive for accuracy, we encourage users to verify important information. The Ordnance survey does not endorse the chatbot’s output.
      </Typography>
    </Card>
    {open && (<ArtifactWindow data={data} open={open} onClose={handleClose}/>)}
    </>
  );
}
