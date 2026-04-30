import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	experimental: {
		proxyTimeout: 300000, // 5 minutes (in milliseconds)
	},
	async rewrites() {
		return [
			{
				source: "/api/:path*",
				destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
			},
		];
	},
};

export default nextConfig;
