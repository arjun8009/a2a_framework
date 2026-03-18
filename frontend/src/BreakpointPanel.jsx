import { useState, useEffect } from "react";
import { io } from "https://cdn.socket.io/4.7.5/socket.io.esm.min.js";
import { Box, Typography, TextField, Button, Chip, Paper } from "@mui/material";
import PauseCircleIcon from "@mui/icons-material/PauseCircle";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

export default function BreakpointPanel({data,onClose}) {
   
    const [suggestion, setSuggestion] = useState("");

    

    const resume = async (withSuggestion) => {
        await fetch("http://localhost:5000/resume-execution", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                suggestion: withSuggestion ? suggestion : null
            }),
        });
        setSuggestion("");
        onClose();
    };

    return (
        <Paper elevation={0} sx={{ m: 2, p: 2, border: "1px solid", borderColor: "warning.main", borderRadius: 2 }}>

            {/* Header */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
                <PauseCircleIcon color="warning" />
                <Typography fontWeight={700} color="warning.dark">
                    Execution Paused
                </Typography>
            </Box>

            {/* Agent + Tool */}
            <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
                <Chip label={`🧠 ${data.agent_name}`} size="small" />
                <Typography sx={{ alignSelf: "center" }}>called</Typography>
                <Chip label={`⚙️ ${data.tool_name}`} size="small" color="primary" />
            </Box>

            {/* Tool args */}
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
                TOOL ARGUMENTS
            </Typography>
            <Box sx={{
                mt: 0.5, mb: 2, p: 1.5, borderRadius: 1,
                background: "#f5f5f5", fontFamily: "monospace", fontSize: 12,
                whiteSpace: "pre-wrap", wordBreak: "break-all"
            }}>
                {JSON.stringify(data.tool_args, null, 2)}
            </Box>

            {/* Suggestion input */}
            <Typography variant="caption" color="text.secondary" fontWeight={600}>
                SUGGEST CHANGES (optional)
            </Typography>
            <TextField
                size="small"
                fullWidth
                multiline
                rows={2}
                placeholder="e.g. Filter by UK region only, limit to 100 rows…"
                value={suggestion}
                onChange={e => setSuggestion(e.target.value)}
                sx={{ mt: 0.5, mb: 2 }}
            />

            {/* Actions */}
            <Box sx={{ display: "flex", gap: 1 }}>
                <Button
                    variant="contained"
                    color="warning"
                    startIcon={<PlayArrowIcon />}
                    onClick={() => resume(false)}
                >
                    Proceed as-is
                </Button>
                <Button
                    variant="contained"
                    color="primary"
                    disabled={!suggestion.trim()}
                    startIcon={<PlayArrowIcon />}
                    onClick={() => resume(true)}
                >
                    Proceed with suggestion
                </Button>
            </Box>

        </Paper>
    );
}