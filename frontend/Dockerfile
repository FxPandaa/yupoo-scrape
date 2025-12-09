# Simple nginx-based frontend
FROM nginx:alpine

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static HTML frontend
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
