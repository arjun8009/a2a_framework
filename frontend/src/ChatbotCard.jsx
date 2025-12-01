import React from "react";
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

export default function ChatbotCard() {
  return (
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
  );
}
