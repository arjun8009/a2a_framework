import React, { useEffect, useState, UseRef, useRef } from "react";

import {
  useTheme,
  useMediaQuery,
  Box,
  TextField,
  Button,
  Typography,
  Avatar,
  Drawer,
  Grid,
  Paper,
  InputAdornment,
  CircularProgress,
  Fab,
  Menu,
  Tooltip
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ReactMarkdown from 'react-markdown';
import IconButton from '@mui/material/IconButton';
import remarkGfm from 'remark-gfm';
import BotIcon from '@mui/icons-material/Android';
import Person from "@mui/icons-material/Person";
import ThreeDotsAnimation from "./threedots";
import MenuIcon from '@mui/icons-material/Menu'
import MenuItem from '@mui/material/MenuItem';
import InputLabel from '@mui/material/InputLabel';
import styled from "@emotion/styled";




export default function ChatUI(){

    /* Here we are setting the states.
        1 input and setInput are for the text field to set and update the text inputs
        2. messages and setMessages are for recording and storing the messages
        3. loading and setLoading are for the loading screen.
        4. artifacts and setArtifacts are for renderring and storing the artifacts
        5. messagesEndRef is for autoscroll to the bottom
        6. isButtonDisabled and setButtonDisabled are to disable the send button if the text field is empty
        7. buttonref is to get a refference to the send button so that enter key can send the message    
    
    */


    const [input, setInput] = useState("")
    const [messages,setMessages] = useState([{"role":"assistant","content":"Hi there!, This is the Ordnance survey chatbot. Please ask a question related to OS NGD Theme"}])
    const [loading,setLoading] = React.useState(false)
    const [artifacts,setArtifacts] = React.useState(null)
    const messagesEndRef = React.useRef(null);
    const [isButtonDisabled, setButtonDisabled] = useState(true);
    const buttonref = useRef()



    const handleSend = async() =>{

        // create the new message
        var message = {role:"user", content:input}
        const updated_messages = [...messages,message]

        // update the messages
        setMessages(updated_messages)
        setInput("") // set input to empty
        setLoading(true) 
        try{
            const url = "http://localhost:5000/receive-data"
            const response = await fetch(url, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body:JSON.stringify({'updated_message':message}),
            });

            if(response.ok){

                // we are expecting the api to return a list of 1 or 2 elements, 1 element indicates some answer and 2 elements indicates [answer, artifact]
                const result = await response.json()
                console.log("Result",result)

                if(result.length==1){
                    setMessages([...updated_messages,result[0]])
                }
                else{

                    setMessages([...updated_messages,result[0],result[1]])
                    setArtifacts(result[1])
                }   
            }else{
                setMessages([...updated_messages,{role:"assistant",content:"Something went wrong"}])    
            }
            setButtonDisabled(true)

        }catch(error){
            setMessages([...updated_messages,{role:"assistant",content:"Something went wrong"}])
        }finally{
            setLoading(false)
        }
    }

    // Rerender component when a new message or artifact is sent and then scroll to bottom
    useEffect(()=>{
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
        console.log("Render when messages need to be updated")
    },[messages,artifacts])


    // When input is changed check if the text field has info then enable send button
    const handleInputChange = (event) => {
    setInput(event.target.value);
    const text = event.target.value
    if(text.length > 0){
      setButtonDisabled(false)
    }else{
      setButtonDisabled(true)
    }
  };

  // support send functionality
  const handelkeypress = (event) => {
    if(event.key=='Enter'){
      buttonref.current.click();
    }
  };
  

    return (
  <Box sx={{
    height: "100%",        
    width: "100%",     
    display: "flex",
    flexDirection: "column",
    bgcolor: "grey.200",
    overflow: "hidden",
  }}>

    {/* Messages container - scrollable */}
    <Box sx={{
      flex: 1,
      overflowY: "auto",
      p: 2,
      display: "flex",
      flexDirection: "column",
      gap: 1,
    }}>
      {messages.map((message, index) => (
        <React.Fragment key={index}>
          <Message message={message} />
        </React.Fragment>
      ))}

      {loading && (
        <Message key="loading" message={{ content: <ThreeDotsAnimation />, role: "assistant" }} />
      )}

      <div ref={messagesEndRef} />
    </Box>

    {/* Input area full width */}
    <Box
      sx={{
        px: 2,          
        py: 2,
        backgroundColor: "background.default",
        borderTop: 1,
        borderColor: "divider",
      }}
    >
      <TextField
        size="small"
        fullWidth
        placeholder="Type a message"
        variant="outlined"
        value={input}
        onKeyDown={handelkeypress}
        onChange={handleInputChange}
        InputProps={{
          endAdornment: (
            <IconButton onClick={handleSend} disabled={isButtonDisabled} ref={buttonref} edge="end">
              <SendIcon />
            </IconButton>
          ),
        }}
      />
    </Box>
  </Box>
);}

const Message = ({message}) => {

    const isBot = message.role === "assistant";
    const renderMessageContent = () => {
  const content = message.content;

  const openInNewTab = () => {
      const blob = new Blob([content], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    };

    // If content is not a string
    if (typeof content !== "string") {
      return <Typography variant="body2">{content}</Typography>;
    }

    // Detect Folium HTML
    const isFoliumHTML =
      content.includes("folium") ||
      content.includes("Leaflet") ||
      content.includes("<script") ||
      content.includes("map_");

    // Detect generic HTML
    const isHTML = /<\/?[a-z][\s\S]*>/i.test(content);

    // Handle Folium (iframe)
    if (isFoliumHTML) {
      return (
        <>
          <button
            onClick={openInNewTab}
            style={{
              marginBottom: "8px",
              padding: "4px 8px",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Open in New Tab
          </button>

          <iframe
            srcDoc={content}
            style={{
              width: "100%",
              height: "400px",
              border: "none",
              borderRadius: "10px",
            }}
          />
        </>
      );
    }

    // Handle generic HTML
    if (isHTML) {
      return (
        <>
          <button
            onClick={openInNewTab}
            style={{
              marginBottom: "8px",
              padding: "4px 8px",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            Open in New Tab
          </button>

          <div dangerouslySetInnerHTML={{ __html: content }} />
        </>
      );
    }

    // Else treat as Markdown
    return (
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    );
  };



    return (
    <Box
       sx={{
      display: "flex",
      justifyContent: isBot ? "flex-start" : "flex-end",
      mb: 1.5,
      width: "100%",
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: isBot ? "row" : "row-reverse",
          alignItems: "flex-start",
          gap: 1,
        }}
      >
        <Avatar 
        sx={{ 
          bgcolor: isBot ? "#4f8ef7" : "#9c27b0",
          width: 32, 
          height: 32 
        }}
      >
        {isBot ? <BotIcon fontSize="small" /> : <Person fontSize="small" />}
      </Avatar>


        {isBot ? (<Paper
            elevation={1}
              sx={{
                p: 2,
                backgroundColor: isBot ? "#f5f5f5" : "#4f8ef7",
                color: isBot ? "black" : "white",
                borderRadius: isBot 
                  ? "20px 20px 20px 5px" 
                  : "20px 20px 5px 20px",
                whiteSpace: "pre-wrap",
                maxWidth: "70%",
                boxShadow: 1,
              }}
            >
            {renderMessageContent()}
            </Paper>) : (
            
            <Paper
            elevation={1}
            sx={{
              p: 2,
              backgroundColor: isBot ? "#f5f5f5" : "#4f8ef7",
              color: isBot ? "black" : "white",
              borderRadius: isBot 
                ? "20px 20px 20px 5px" 
                : "20px 20px 5px 20px",
              whiteSpace: "pre-wrap",
              maxWidth: "70%",
              boxShadow: 1,
            }}
            >
             {renderMessageContent()} 
            
          </Paper>
        )}
        
        </Box>
      </Box>
  );

}
