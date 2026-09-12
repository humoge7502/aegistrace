"use client";

import { useMemo, useRef, useState } from "react";

import { stateColor } from "@/lib/trust";

export type GraphNode = {
  id: string;
  type: string;
  label: string;
  trust_state: string;
  component_kind?: string;
  deviation?: boolean;
  digest?: string | null;
  quarantined?: boolean;
};
export type GraphEdge = {
  src: string;
  dst: string;
  kind: string;
  seq: number | null;
  expected: boolean;
};

const NODE_W = 132;
const NODE_H = 46;
const COL_X = [60, 260, 480];

function shapeFor(node: GraphNode): string {
  if (node.type === "execution") return "squircle";
  if (node.type === "output") return "circle-dashed";
  switch (node.component_kind) {
    case "model": return "circle";
    case "mcp_server": return "diamond";
    case "tool": return "hexagon";
    case "corpus": return "cylinder";
    default: return "rect";
  }
}

export default function GraphViewer({ nodes, edges }: { nodes: GraphNode[]; edges: GraphEdge[] }) {
  const [selected, setSelected] = useState<GraphNode | null>(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const drag = useRef<{ x: number; y: number } | null>(null);

  const layout = useMemo(() => {
    const pos: Record<string, { x: number; y: number }> = {};
    const executions = nodes.filter((n) => n.type === "execution");
    const outputs = nodes.filter((n) => n.type === "output");
    const components = nodes.filter((n) => n.type === "component");
    const compOrder = [...components].sort((a, b) => {
      const ea = edges.find((e) => e.dst === a.id)?.seq ?? 99;
      const eb = edges.find((e) => e.dst === b.id)?.seq ?? 99;
      return ea - eb;
    });
    executions.forEach((n, i) => { pos[n.id] = { x: COL_X[0], y: 60 + i * (NODE_H + 34) }; });
    compOrder.forEach((n, i) => { pos[n.id] = { x: COL_X[1], y: 20 + i * (NODE_H + 22) }; });
    outputs.forEach((n, i) => { pos[n.id] = { x: COL_X[2], y: 60 + i * (NODE_H + 34) }; });
    return pos;
  }, [nodes, edges]);

  const height = useMemo(() => {
    const maxY = Math.max(...Object.values(layout).map((p) => p.y), 200);
    return maxY + NODE_H + 60;
  }, [layout]);

  function nodeShape(node: GraphNode, pos: { x: number; y: number }) {
    const color = stateColor(node.trust_state);
    const fill = `${color}22`;
    const stroke = node.deviation ? "#f87171" : color;
    const cx = pos.x + NODE_W / 2;
    const cy = pos.y + NODE_H / 2;
    const s = shapeFor(node);
    const common = { fill, stroke, strokeWidth: 1.5 };
    switch (s) {
      case "circle":
        return <circle cx={cx} cy={cy} r={26} {...common} />;
      case "circle-dashed":
        return <circle cx={cx} cy={cy} r={26} {...common} strokeDasharray="5 4" />;
      case "diamond":
        return <rect x={pos.x + 14} y={pos.y} width={NODE_W - 28} height={NODE_H} rx={6} transform={`rotate(0 ${cx} ${cy})`} {...common} />;
      case "hexagon":
        return <polygon points={hexPoints(cx, cy, 30, 24)} {...common} />;
      case "cylinder":
        return (
          <g>
            <rect x={pos.x + 10} y={pos.y + 4} width={NODE_W - 20} height={NODE_H - 8} rx={14} {...common} />
            <line x1={pos.x + 10} y1={pos.y + 10} x2={pos.x + NODE_W - 10} y2={pos.y + 10} stroke={stroke} strokeWidth={1} />
          </g>
        );
      case "squircle":
        return <rect x={pos.x} y={pos.y} width={NODE_W} height={NODE_H} rx={14} {...common} strokeWidth={2} />;
      default:
        return <rect x={pos.x + 8} y={pos.y} width={NODE_W - 16} height={NODE_H} rx={8} {...common} />;
    }
  }

  return (
    <div>
      <div
        className="dotgrid relative overflow-hidden rounded-lg border border-hairline"
        role="application"
        aria-label="Trust graph. Use the table below for a text alternative."
      >
        <div className="absolute right-2 top-2 z-10 flex gap-1">
          <button aria-label="Zoom in" className="rounded border border-hairline bg-surface px-2 py-0.5 text-sm hover:text-accent" onClick={() => setZoom((z) => Math.min(2, z + 0.15))}>+</button>
          <button aria-label="Zoom out" className="rounded border border-hairline bg-surface px-2 py-0.5 text-sm hover:text-accent" onClick={() => setZoom((z) => Math.max(0.5, z - 0.15))}>−</button>
          <button aria-label="Reset view" className="rounded border border-hairline bg-surface px-2 py-0.5 text-xs text-ink-dim hover:text-accent" onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}>reset</button>
        </div>
        <svg
          viewBox={`0 0 ${COL_X[2] + NODE_W + 60} ${height}`}
          className="w-full cursor-grab active:cursor-grabbing"
          style={{ maxHeight: 460 }}
          tabIndex={0}
          role="group"
          aria-label="Causal trust graph"
          onWheel={(e) => {
            if (!e.ctrlKey && Math.abs(e.deltaY) < 10) return;
            e.preventDefault();
            setZoom((z) => Math.min(2, Math.max(0.5, z - Math.sign(e.deltaY) * 0.1)));
          }}
          onPointerDown={(e) => { drag.current = { x: e.clientX - pan.x, y: e.clientY - pan.y }; }}
          onPointerUp={() => { drag.current = null; }}
          onPointerLeave={() => { drag.current = null; }}
          onPointerMove={(e) => {
            if (drag.current) setPan({ x: e.clientX - drag.current.x, y: e.clientY - drag.current.y });
          }}
        >
          <g transform={`translate(${pan.x} ${pan.y}) scale(${zoom})`}>
            {/* edges */}
            {edges.map((e, i) => {
              const a = layout[e.src];
              const b = layout[e.dst];
              if (!a || !b) return null;
              const x1 = a.x + (e.src.startsWith("component:") ? NODE_W / 2 : NODE_W);
              const y1 = a.y + NODE_H / 2;
              const x2 = e.src.startsWith("component:") ? b.x + NODE_W / 2 : b.x;
              const y2 = b.y + NODE_H / 2;
              const mx = (x1 + x2) / 2;
              const color = e.expected ? "#4ade80" : "#f87171";
              return (
                <g key={i}>
                  <path
                    d={`M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`}
                    fill="none"
                    stroke={color}
                    strokeOpacity={e.expected ? 0.45 : 0.95}
                    strokeWidth={e.expected ? 1.4 : 2}
                    strokeDasharray={e.expected ? undefined : "6 6"}
                    className={e.expected ? undefined : "dev-edge"}
                  />
                  {e.seq != null && e.kind === "step" ? (
                    <text x={mx} y={(y1 + y2) / 2 - 5} textAnchor="middle" fill="#5b6474" fontSize={9} fontFamily="monospace">
                      {e.seq}
                    </text>
                  ) : null}
                </g>
              );
            })}
            {/* nodes */}
            {nodes.map((n) => {
              const pos = layout[n.id];
              if (!pos) return null;
              return (
                <g
                  key={n.id}
                  role="button"
                  tabIndex={0}
                  aria-label={`${n.type} ${n.label}, trust state ${n.trust_state}${n.deviation ? ", deviation detected" : ""}`}
                  onClick={() => setSelected(n)}
                  onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") setSelected(n); }}
                  className="cursor-pointer"
                >
                  {nodeShape(n, pos)}
                  <text x={pos.x + NODE_W / 2} y={pos.y + 19} textAnchor="middle" fill="#e6eaf2" fontSize={11} fontWeight={600}>
                    {truncate(n.label, 16)}
                  </text>
                  <text x={pos.x + NODE_W / 2} y={pos.y + 34} textAnchor="middle" fill={stateColor(n.trust_state)} fontSize={9} fontFamily="monospace">
                    {n.trust_state}
                  </text>
                  {n.deviation ? (
                    <circle cx={pos.x + 6} cy={pos.y + 4} r={5} fill="#f87171">
                      <animate attributeName="opacity" values="1;0.4;1" dur="1.6s" repeatCount="indefinite" />
                    </circle>
                  ) : null}
                </g>
              );
            })}
          </g>
        </svg>
      </div>

      {/* a11y: text alternative */}
      <details className="mt-2">
        <summary className="cursor-pointer text-xs text-ink-faint">Text alternative (nodes & edges)</summary>
        <table className="mt-2 w-full text-xs">
          <thead><tr className="text-left text-ink-faint"><th className="py-1">Node</th><th>Type</th><th>Trust state</th><th>Deviation</th></tr></thead>
          <tbody>
            {nodes.map((n) => (
              <tr key={n.id} className="border-t border-hairline/50">
                <td className="mono py-1">{n.label}</td><td>{n.type}</td><td>{n.trust_state}</td><td>{n.deviation ? "yes" : "no"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>

      {/* selected node panel */}
      {selected ? (
        <div className="mt-3 rounded-lg border border-hairline bg-surface-2 p-4">
          <div className="flex items-center justify-between">
            <div className="microlabel">{selected.type}</div>
            <button className="text-xs text-ink-faint hover:text-ink" onClick={() => setSelected(null)}>close</button>
          </div>
          <div className="mono mt-1 text-sm">{selected.label}</div>
          <div className="mt-1 text-xs text-ink-dim">trust state: {selected.trust_state}</div>
          {selected.digest ? <div className="mono mt-1 break-all text-xs text-ink-faint">{selected.digest}</div> : null}
        </div>
      ) : null}
    </div>
  );
}

function truncate(s: string, n: number): string {
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
}

function hexPoints(cx: number, cy: number, rx: number, ry: number): string {
  const pts: string[] = [];
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i - Math.PI / 2;
    pts.push(`${cx + rx * Math.cos(angle)},${cy + ry * Math.sin(angle)}`);
  }
  return pts.join(" ");
}
