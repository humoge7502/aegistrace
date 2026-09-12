import { ImageResponse } from "next/og";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "AegisTrace — continuous AI execution attestation";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#0b0e14",
          color: "#e6eaf2",
          padding: 64,
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <svg width="40" height="40" viewBox="0 0 26 26">
            <path d="M13 1.5 23 5.5v7c0 6-4.4 10.4-10 12C7.4 22.9 3 18.5 3 12.5v-7L13 1.5Z" fill="#22d3ee" fillOpacity="0.12" stroke="#22d3ee" strokeWidth="1.5" />
            <path d="M8 13.2l3.4 3.4L18.5 9.5" stroke="#22d3ee" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <div style={{ display: "flex", fontSize: 26, fontWeight: 700, letterSpacing: -0.5 }}>AegisTrace</div>
          <div style={{ display: "flex", marginLeft: "auto", color: "#5b6474", fontSize: 15, fontFamily: "monospace" }}>ATTEST/SYS v0.1.0</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ display: "flex", fontSize: 78, fontWeight: 700, letterSpacing: -3, lineHeight: 1.02 }}>Every output</div>
          <div style={{ display: "flex", fontSize: 78, fontWeight: 700, letterSpacing: -3, lineHeight: 1.02 }}>
            has a&nbsp;<span style={{ display: "flex", color: "#22d3ee" }}>past.</span>
          </div>
          <div style={{ display: "flex", marginTop: 28, fontSize: 23, color: "#9aa3b5", maxWidth: 820 }}>
            Runtime causal trust for AI agents — provenance graphs, expected-vs-observed verification, and verifiable per-execution certificates.
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", color: "#5b6474", fontSize: 15, fontFamily: "monospace" }}>
          <div style={{ display: "flex" }}>unknown ≠ trusted</div>
          <div style={{ display: "flex" }}>predicate aegistrace.dev/attestations/execution-trust/v1</div>
        </div>
      </div>
    ),
    size,
  );
}
