import type { NextConfig } from "next";
import dotenv from "dotenv";
dotenv.config({ path: "../.env" });

const nextConfig: NextConfig = {
  images: {
    unoptimized: true,
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn.jkdesu.com",
      },
      {
        protocol: "https",
        hostname: "i.ibb.co",
      },
    ],
  },
};

export default nextConfig;
