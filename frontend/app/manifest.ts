import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "AegisTrace Console",
    short_name: "AegisTrace",
    description: "Continuous AI execution attestation and runtime causal trust.",
    start_url: "/app",
    display: "standalone",
    background_color: "#0b0e14",
    theme_color: "#0b0e14",
    icons: [{ src: "/favicon.ico", sizes: "any", type: "image/x-icon" }],
  };
}
