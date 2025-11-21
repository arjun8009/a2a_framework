import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

export default function AgentGraphLive() {
  const svgRef = useRef();
  const [agents, setAgents] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [selectedLink, setSelectedLink] = useState(null);
  const [hoveredAgent, setHoveredAgent] = useState(null);
  const simulationRef = useRef(null);
  const [activeMessage, setActiveMessage] = useState(null);


  const AgentCard = ({ agent }) => (
  <div className="bg-white shadow-md border border-gray-300 p-3 rounded-lg w-60 text-sm">
    <h3 className="font-semibold text-blue-700">{agent.agent_name}</h3>
    <p className="text-gray-600 mb-2">{agent.agent_description}</p>
    <div className="text-xs">
      <strong>Capabilities:</strong> {agent.capabilities.join(", ")}<br />
      <strong>Input:</strong> {agent.input_modes.join(", ")}<br />
      <strong>Output:</strong> {agent.output_modes.join(", ")}
    </div>
  </div>
);


  useEffect(() => {
    socket.on("agents_init", (data) => setAgents(data));

    socket.on("new_interaction", (interaction) => {
      console.log("interaction received",interaction)
      setInteractions((prev) => [...prev, interaction]);
      setActiveMessage(`${interaction.source} → ${interaction.target}: ${interaction.msg}`);

    });

    return () => {
      socket.off("agents_init");
      socket.off("new_interaction");
    };
  }, []);

  useEffect(() => {
    if (!agents.length) return;

    const width = 800, height = 600;
    const color = d3.schemeSet2[Math.floor(Math.random() * 8)];
    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])
       .attr("width", "100%")
      .attr("height", "100%")
      .attr("class", "bg-gray-50")
      .style("overflow", "hidden");

    svg.selectAll("*").remove();

    const defs = svg.append("defs");

    defs.append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 10) // ~ circle radius + offset
      .attr("refY", 0)
      .attr("markerWidth", 8)
      .attr("markerHeight", 8)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", color);


    const simulation = d3.forceSimulation(agents)
      .force("link", d3.forceLink(interactions).id(d => d.agent_name).distance(190))
      .force("charge", d3.forceManyBody().strength(-150))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("x", d3.forceX(width / 2).strength(0.04))  // keeps nodes towards center horizontally
      .force("y", d3.forceY(height / 2).strength(0.04))
      .alphaDecay(0.05);

    simulationRef.current = simulation;

    const link = svg.append("g")
      .attr("stroke", "#666")
      .attr("stroke-opacity", 0.8)
      .selectAll("path")
      .data(interactions)
      .join("path")
      .attr("stroke-width", 2)
      .attr("fill", "none")
      .attr("marker-end", "url(#arrow)") // directed
      .on("click", (_, d) => setSelectedLink(d));

    const node = svg.append("g")
      .selectAll("g")
      .data(agents)
      .join("g")
       .style("cursor", "pointer")
  .on("mouseover", (_, d) => setHoveredAgent(d))
  .on("mouseout", () => setHoveredAgent(null))
  .on("click", (_, d) => setSelectedLink(d));
    
    node.append("circle")
    .attr("r", 40)
    .attr("fill", (d, i) => d3.schemeSet2[i % 8]);

    node.append("text")
    .text(d=>d.agent_name)
    .attr("text-anchor", "middle")
    .attr("alignment-baseline", "middle")  // vertically center
    .attr("font-size", 10)
    .attr("fill", "white");  // contrast color for visibility



  simulation.on("tick", () => {
  node.attr("transform", d => `translate(${d.x},${d.y})`);
  



  link.attr("d", d => {
  const r = 40; // node radius
  const sx = d.source.x;
  const sy = d.source.y;
  const tx = d.target.x;
  const ty = d.target.y;

  const dx = tx - sx;
  const dy = ty - sy;
  const dr = Math.sqrt(dx * dx + dy * dy);

  const nx = dx / dr;
  const ny = dy / dr;

  const startX = sx + nx * r;
  const startY = sy + ny * r;
  const endX = tx - nx * r;
  const endY = ty - ny * r;

  // multiple links, including opposite directions
  const sameLinks = interactions.filter(
    l =>
      (l.source.agent_name === d.source.agent_name && l.target.agent_name === d.target.agent_name) ||
      (l.source.agent_name === d.target.agent_name && l.target.agent_name === d.source.agent_name)
  );
  const index = sameLinks.findIndex(l => l === d);

  const curveStrength = 25 * (index - (sameLinks.length - 1) / 2) * (d.source.agent_name > d.target.agent_name ? 1 : -1);

  // perpendicular offset
  const offsetX = -ny * curveStrength;
  const offsetY = nx * curveStrength;
  const controlX = (startX + endX) / 2 + offsetX;
  const controlY = (startY + endY) / 2 + offsetY;

  return `M${startX},${startY} Q${controlX},${controlY} ${endX},${endY}`;
});

});


  }, [agents, interactions]);

  return (
    <div className="relative flex justify-center items-center h-screen w-screen overflow-hidden">
      <svg ref={svgRef} width="100%" height="100%" style={{"overflow":"hidden"}} />
      {selectedLink && (
        <div className="absolute top-5 left-1/2 -translate-x-1/2 bg-white border border-gray-300 shadow-lg p-3 rounded-lg w-72 text-sm">
          <div className="flex justify-between items-center mb-2">
            <strong>{selectedLink.source.name} → {selectedLink.target.name}</strong>
            <button onClick={() => setSelectedLink(null)}>✕</button>
          </div>
          <p><strong>Message:</strong> {selectedLink.msg}</p>
          
        </div>
      )}
      {activeMessage && (
  <div className="absolute bottom-5 left-1/2 -translate-x-1/2 bg-white border border-gray-300 shadow-lg p-3 rounded-lg w-72 text-sm">
    <p>{activeMessage}</p>
  </div>
)}
    </div>
  );
}