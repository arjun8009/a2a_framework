import { useState, useEffect, useRef } from "react";
import { io } from "socket.io-client";
import BreakpointPanel from "./BreakpointPanel";
import { createPortal } from "react-dom";

const SOCKET_URL = "http://localhost:5000";

const PALETTE = [
  { bg: "rgba(124,58,237,0.12)", border: "#7C3AED", text: "#A78BFA" },
  { bg: "rgba(14,165,233,0.12)",  border: "#0EA5E9", text: "#38BDF8" },
  { bg: "rgba(16,185,129,0.12)",  border: "#10B981", text: "#34D399" },
  { bg: "rgba(245,158,11,0.12)",  border: "#F59E0B", text: "#FCD34D" },
  { bg: "rgba(236,72,153,0.12)",  border: "#EC4899", text: "#F9A8D4" },
];

function makeColorMap() {
  const map = {}, palette = PALETTE;
  let idx = 0;
  return (name) => {
    if (!map[name]) map[name] = palette[idx++ % palette.length];
    return map[name];
  };
}


// ── Table shown when row is expanded ─────────────────────────────────────────
function DBTable({ columns, conditions }) {
  return (
    <div style={{ borderRadius: 8, overflow: "hidden", border: "1px solid rgba(255,255,255,0.08)" }}>
      {/* thead */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", background: "rgba(255,255,255,0.05)", borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
        {["Column", "Condition"].map(h => (
          <div key={h} style={{ padding: "7px 14px", fontSize: 10, fontWeight: 700, letterSpacing: "0.1em", textTransform: "uppercase", color: "rgba(255,255,255,0.35)" }}>{h}</div>
        ))}
      </div>
      {/* rows */}
      {columns.map((col, i) => (
        <div key={i} style={{
          display: "grid", gridTemplateColumns: "1fr 1fr",
          background: i % 2 === 0 ? "rgba(255,255,255,0.015)" : "transparent",
          borderBottom: i < columns.length - 1 ? "1px solid rgba(255,255,255,0.04)" : "none",
        }}>
          <div style={{ padding: "8px 14px", fontSize: 12, color: "#86EFAC", fontFamily: "monospace" }}>{col}</div>
          <div style={{ padding: "8px 14px", fontSize: 12, fontFamily: "monospace", color: conditions[i] ? "#FCD34D" : "rgba(255,255,255,0.2)", fontStyle: conditions[i] ? "normal" : "italic" }}>
            {conditions[i] || "—"}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Single expandable call row ────────────────────────────────────────────────
function CallRow({ call, index, isNew, getColor }) {
  const [open, setOpen] = useState(false);
  const ac = getColor(call.agent_name);
  const [showBreakpoint, setShowBreakpoint] = useState(false);
  const colCount = call.table.columns.length;
  const condCount = call.table.conditions.filter(Boolean).length;

  return (
    <div style={{
      borderRadius: 10,
      border: `1px solid ${open ? ac.border + "55" : "rgba(255,255,255,0.08)"}`,
      background: open ? ac.bg : "rgba(255,255,255,0.025)",
      transition: "border-color 0.2s, background 0.2s",
      animation: isNew ? "slideIn 0.28s ease" : "none",
      overflow: "hidden",
    }}>
      {/* Row header */}
      <div
        onClick={() => setOpen(o => !o)}
        style={{ display: "flex", alignItems: "center", gap: 10, padding: "11px 14px", cursor: "pointer", userSelect: "none" }}
      >
        {/* Index */}
        <span style={{ fontSize: 10, color: "rgba(255,255,255,0.25)", fontFamily: "monospace", minWidth: 24 }}>#{index + 1}</span>

        {/* Agent */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "3px 10px", borderRadius: 20, background: ac.bg, border: `1px solid ${ac.border}44`, flexShrink: 0 }}>
          <span style={{ fontSize: 12 }}>🧠</span>
          <span style={{ fontSize: 12, fontWeight: 600, color: ac.text }}>{call.agent_name}</span>
        </div>

        <span style={{ color: "rgba(255,255,255,0.2)", fontSize: 12 }}>→</span>

        {/* Database */}
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "3px 10px", borderRadius: 20, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.25)", flexShrink: 0 }}>
          <span style={{ fontSize: 12 }}>🗄️</span>
          <span style={{ fontSize: 12, fontWeight: 600, color: "#34D399" }}>{call.database_name}</span>
        </div>

        <div style={{ flex: 1 }} />

        {/* Counts */}
        <span style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", background: "rgba(255,255,255,0.05)", padding: "2px 8px", borderRadius: 4 }}>
          {colCount} cols
        </span>
        <span style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", background: "rgba(255,255,255,0.05)", padding: "2px 8px", borderRadius: 4 }}>
          {condCount} conditions
        </span>

        {/* Chevron */}
        <span style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", transform: open ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 0.2s", display: "inline-block" }}>▼</span>
      </div>

      {/* Expanded table */}
      {open && (
        <div style={{ padding: "0 14px 12px", animation: "expandDown 0.2s ease" }}>
          <DBTable columns={call.table.columns} conditions={call.table.conditions} />
        </div>
      )}
        {/* ── Check Arguments button — only when paused ── */}
      {call.pause && (
        <div style={{ padding: "0 14px 12px" }}>
          <button
            onClick={(e) => { e.stopPropagation(); setShowBreakpoint(true); }}
            style={{
              width: "100%", padding: "7px 0", borderRadius: 7,
              border: "1px solid rgba(245,158,11,0.4)",
              background: "rgba(245,158,11,0.08)",
              color: "#FCD34D", fontSize: 12, fontWeight: 600,
              cursor: "pointer", fontFamily: "inherit",
            }}
          >
            ⏸ Check Arguments
          </button>
        </div>
      )}

      {/* ── Breakpoint panel modal ── */}
      {showBreakpoint && createPortal(
    <div
        onClick={() => setShowBreakpoint(false)}
        style={{
            position: "fixed", inset: 0,
            background: "rgba(0,0,0,0.5)",
            zIndex: 9999,
            display: "flex", alignItems: "center", justifyContent: "center",
        }}
    >
        <div onClick={e => e.stopPropagation()}>
            <BreakpointPanel
                data={{
                    agent_name: call.agent_name,
                    tool_name: call.database_name,
                    tool_args: call.tool_args,
                }}
                onClose={() => setShowBreakpoint(false)}
            />
        </div>
    </div>,
    document.body
)}
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────
export default function CodeAgentPanel() {
  const [calls, setCalls]         = useState([]);
  const [newIdx, setNewIdx]       = useState(-1);
  const [connected, setConnected] = useState(false);
  const getColor                  = useRef(makeColorMap()).current;
  const listRef                   = useRef(null);

  useEffect(() => {
    const socket = io(SOCKET_URL, { transports: ["websocket"] });
    socket.on("connect",    () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));
    socket.on("new_code_data", (payload) => {
      if (!payload?.agent_name || !payload?.database_name || !payload?.table) return;
      setCalls(prev => {
        const next = [...prev, { ...payload, _id: Date.now() + Math.random() }];
        setNewIdx(next.length - 1);
        setTimeout(() => setNewIdx(-1), 400);
        return next;
      });
    });
    return () => socket.disconnect();
  }, []);

  useEffect(() => {
    if (listRef.current) listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [calls]);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        @keyframes slideIn    { from { opacity:0; transform:translateY(-8px) } to { opacity:1; transform:translateY(0) } }
        @keyframes expandDown { from { opacity:0; transform:scaleY(0.95); transform-origin:top } to { opacity:1; transform:scaleY(1) } }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
      `}</style>

      <div style={{
        width: "100%", flex:1,
        minHeight:0,
        background: "#0F1117",
        borderRadius: 14,
        border: "1px solid rgba(255,255,255,0.08)",
        display: "flex", flexDirection: "column",
        fontFamily: "'Inter', sans-serif",
        overflow: "hidden",
      }}>

        {/* ── Header ── */}
        <div style={{
          padding: "16px 20px",
          borderBottom: "1px solid rgba(255,255,255,0.07)",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          background: "rgba(255,255,255,0.02)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ fontSize: 18 }}>🗄️</div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: "rgba(255,255,255,0.9)" }}>Database Calls</div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.35)", marginTop: 1 }}>
                {calls.length === 0 ? "No calls yet" : `${calls.length} call${calls.length !== 1 ? "s" : ""} recorded`}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* Socket status */}
            <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{
                width: 6, height: 6, borderRadius: "50%",
                background: connected ? "#10B981" : "#6B7280",
                boxShadow: connected ? "0 0 6px #10B98177" : "none",
              }} />
              <span style={{ fontSize: 11, color: connected ? "#34D399" : "rgba(255,255,255,0.25)" }}>
                {connected ? "Live" : "Offline"}
              </span>
            </div>

            {calls.length > 0 && (
              <>
                <div style={{ width: 1, height: 14, background: "rgba(255,255,255,0.1)" }} />
                <button
                  onClick={() => setCalls([])}
                  style={{ background: "none", border: "none", color: "rgba(255,255,255,0.3)", fontSize: 11, cursor: "pointer", fontFamily: "inherit", padding: "2px 4px" }}
                >Clear</button>
              </>
            )}
          </div>
        </div>

        {/* ── Rows ── */}
        <div ref={listRef} style={{ flex: 1, overflow: "auto", padding: "12px 14px"}}>
          {calls.length === 0 ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10, color: "rgba(255,255,255,0.15)" }}>
              <span style={{ fontSize: 32 }}>🗄️</span>
              <span style={{ fontSize: 12 }}>Waiting for database calls…</span>
            </div>
          ) : (
            calls.map((call, i) => (
              <div key={call._id} style={{ marginBottom: 7 }}>
              <CallRow key={call._id} call={call} index={i} isNew={newIdx === i} getColor={getColor} />
              </div>
            ))
          )}
        </div>

      </div>
    </>
  );
}