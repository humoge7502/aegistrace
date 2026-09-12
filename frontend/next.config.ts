import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // standalone bundle is produced only for Docker builds (deploy/Dockerfile.frontend)
  ...(process.env.STANDALONE === "1" ? { output: "standalone" as const } : {}),
};

export default nextConfig;
