/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
    images: {
      domains: ['localhost'],
    },
    // Set environment variables available to the client
    env: {
      // Default to local backend if not specified
      BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:5000',
    },
  };
  
  module.exports = nextConfig;