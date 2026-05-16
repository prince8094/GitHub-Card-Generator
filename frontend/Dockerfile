# Use nginx to serve the static frontend
FROM nginx:alpine

# Copy the frontend file
COPY index.html /usr/share/nginx/html/index.html

# We use a script to replace the backend URL if provided as an ENV var
# However, for simplicity in this single-file setup, we'll keep it as is
# or use a simple sed command at start.
CMD ["nginx", "-g", "daemon off;"]
