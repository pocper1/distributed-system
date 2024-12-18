# Stage 1: Build the React application
FROM node:16 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the container and install dependencies
COPY app/package*.json /app
RUN npm install

ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Build the React application for production
COPY app/public /app/public/
COPY app/src /app/src/
COPY app/.env /app/
RUN npm run build


# Stage 2: Serve the built files using Nginx
FROM nginx:alpine

# Copy the built files from the previous stage to the Nginx default directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose the default Nginx HTTP port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
