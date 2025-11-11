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
    });

    return () => {
      socket.off("agents_init");
      socket.off("new_interaction");
    };
  }, []);

  useEffect(() => {
    if (!agents.length) return;

    const width = 800, height = 600;
    const svg = d3.select(svgRef.current)
      .attr("viewBox", [0, 0, width, height])
       .attr("width", "100%")
      .attr("height", "100%")
      .attr("class", "bg-gray-50")
      .style("overflow", "hidden");

    svg.selectAll("*").remove();

    const simulation = d3.forceSimulation(agents)
      .force("link", d3.forceLink(interactions).id(d => d.agent_name).distance(150))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("x", d3.forceX(width / 2).strength(0.1))  // keeps nodes towards center horizontally
      .force("y", d3.forceY(height / 2).strength(0.1));

    simulationRef.current = simulation;

    const link = svg.append("g")
      .selectAll("line")
      .data(interactions)
      .join("line")
      .attr("stroke", "#aaa")
      .attr("stroke-width", 2)
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
      link
        .attr("x1", (d) => d.source.x)
        .attr("y1", (d) => d.source.y)
        .attr("x2", (d) => d.target.x)
        .attr("y2", (d) => d.target.y);
      node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
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
      {hoveredAgent && (
  <div
    className="absolute bg-white border border-gray-300 shadow-lg p-3 rounded-lg w-60 text-sm pointer-events-none"
    style={{
      left: `${hoveredAgent.x + 25}px`, // 25px offset to the right of the node
      top: `${hoveredAgent.y - 20}px`,  // 20px offset above the node
    }}
  >
    <AgentCard agent={hoveredAgent} />
  </div>)}
    </div>
  );
}