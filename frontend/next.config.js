/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
    
    // Replace deprecated images.domains with remotePatterns
    images: {
      remotePatterns: [
        {
          protocol: 'http',
          hostname: 'localhost',
        },
      ],
    },
    
    // Environment variables
    env: {
      BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:5000',
    },
};
  
module.exports = nextConfig;