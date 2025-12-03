import React, { useState } from "react";
import { Button, Dialog, DialogTitle, DialogContent, DialogActions, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';
import BasicTable from "./Table";

export default function ArtifactWindow({data, messages, open, onClose }) {

  const [isFullScreen, setIsFullScreen] = useState(false);
  console.log("In window",messages)
  console.log("In Window",data)
  const newmessages = messages.filter(item => item.role === 'user');
  function createData(question,sources){
    return {
      question,
      sources:sources
    }
  }

  const rows = newmessages.map((question, index) => createData(question.content, data[index].sources));
  console.log("In window",rows)


  const handleToggleFullScreen = () => {
    setIsFullScreen(!isFullScreen);
  };
  return (
    <div>
      <Dialog open={open} onClose={onClose} fullWidth fullScreen={isFullScreen}>
        <DialogTitle>
          Sources Dialog
          <IconButton
            color="default"
            style={{ position: "absolute", right: "65px", top: "8px" }}
            onClick={handleToggleFullScreen}
          >
            {isFullScreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
          </IconButton>
          <Button
            variant="text"
            color="error"
            style={{ position: "absolute", right: "8px", top: "8px" }}
            onClick={onClose}
          >
            <CloseIcon />
          </Button>
        </DialogTitle>
        <DialogContent>
          <BasicTable rows={rows}/>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
