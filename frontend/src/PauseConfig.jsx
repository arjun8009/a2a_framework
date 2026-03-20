import React, { useState } from "react";
import { Button, Box, Dialog, Paper, FormControl, InputLabel, Select, MenuItem, OutlinedInput, Chip,Divider, DialogTitle, DialogContent, DialogActions, IconButton, Typography } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';

function PauseMenuConfig({ data }) {
  // Parse data prop
  const choice1Data = data[0].agent
  const choice2Data = data[1].tools
 
  const [formType, setFormType] = useState("");
  const [fieldSelections, setFieldSelections] = useState({});        // for choice 1
  const [choice2Selection, setChoice2Selection] = useState([]);      // for choice 2
  const [status, setStatus] = useState(null);
 
  // ── helpers ────────────────────────────────────────────────────────────────
 
  const handleFieldChange = (fieldName, value) => {
    setFieldSelections((prev) => ({ ...prev, [fieldName]: value }));
  };
 
  const buildPayload = () => {
    if (formType === 1) {
      return { choice: 1, data: fieldSelections };
    }
    return { choice: 2, data: choice2Selection };
  };
 
  const handleSubmit = async () => {
    setStatus("loading");
    try {
      const res = await fetch("http://localhost:5000/set-pause-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload()),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setStatus("success");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };
 
  // ── render ─────────────────────────────────────────────────────────────────
 
  return (
    <Paper elevation={3} sx={{ maxWidth: 520, mx: "auto", mt: 4, p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Pause Menu Config
      </Typography>
      <Divider sx={{ mb: 2 }} />
 
      {/* Form type selector */}
      <FormControl fullWidth size="small">
        <InputLabel>Form Type</InputLabel>
        <Select
          value={formType}
          label="Form Type"
          onChange={(e) => {
            setFormType(e.target.value);
            setFieldSelections({});
            setChoice2Selection([]);
            setStatus(null);
          }}
        >
          <MenuItem value={1}>Customize view</MenuItem>
          <MenuItem value={2}>Simplified view</MenuItem>
        </Select>
      </FormControl>
 
      {/* ── Choice 1: one multi-select per field ── */}
      {formType === 1 && (
        <Box sx={{ mt: 2, display: "flex", flexDirection: "column", gap: 2 }}>
          {Object.entries(choice1Data).map(([fieldName, options]) => (
            <FormControl key={fieldName} fullWidth size="small">
              <InputLabel>{fieldName}</InputLabel>
              <Select
                multiple
                value={fieldSelections[fieldName] ?? []}
                onChange={(e) => handleFieldChange(fieldName, e.target.value)}
                input={<OutlinedInput label={fieldName} />}
                renderValue={(selected) => (
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                    {selected.map((val) => (
                      <Chip key={val} label={val} size="small" />
                    ))}
                  </Box>
                )}
              >
                {options.map((opt) => (
                  <MenuItem key={opt} value={opt}>
                    {opt}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          ))}
        </Box>
      )}
 
      {/* ── Choice 2: single multi-select ── */}
      {formType === 2 && (
        <Box sx={{ mt: 2 }}>
          <FormControl fullWidth size="small">
            <InputLabel>Options</InputLabel>
            <Select
              multiple
              value={choice2Selection}
              onChange={(e) => setChoice2Selection(e.target.value)}
              input={<OutlinedInput label="Options" />}
              renderValue={(selected) => (
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                  {selected.map((val) => (
                    <Chip key={val} label={val} size="small" />
                  ))}
                </Box>
              )}
            >
              {choice2Data.map((opt) => (
                <MenuItem key={opt} value={opt}>
                  {opt}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      )}
 
      {/* Submit */}
      {formType !== "" && (
        <Box sx={{ mt: 3, display: "flex", alignItems: "center", gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={status === "loading"}
          >
            {status === "loading" ? "Submitting…" : "Submit"}
          </Button>
          {status === "success" && (
            <Typography variant="body2" color="success.main">
              Submitted successfully.
            </Typography>
          )}
          {status === "error" && (
            <Typography variant="body2" color="error">
              Submission failed.
            </Typography>
          )}
        </Box>
      )}
    </Paper>
  );
}


export default function PauseConfig({data, open, onClose}){

    const [isFullScreen, setIsFullScreen] = useState(false)

    const handleToggleFullScreen = () => {
    setIsFullScreen(!isFullScreen);
  };

  return (
    <div>
      <Dialog open={open} onClose={onClose} fullWidth fullScreen={isFullScreen}>
        <DialogTitle>
          Config Dialog
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
            {!data ? (<Typography variant="h2">Invalid config</Typography>):(<PauseMenuConfig data={data} />)}
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