import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/auth/:path",
        destination: "http://127.0.0.1:8000/auth/:path"
      }
    ]
  }
};

export default nextConfig;
