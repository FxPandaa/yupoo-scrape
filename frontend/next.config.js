/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['photo.yupoo.com', 'x.yupoo.com', 'yupoo.com'],
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://api:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
