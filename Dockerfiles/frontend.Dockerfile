# Stage 1: Build the React application
FROM node:16 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the container and install dependencies
COPY app/package*.json /app
RUN npm install

# Build the React application for production
COPY app/public /app/public/
COPY app/src /app/src/
COPY app/.env /app/
RUN npm run build

# Stage 2: Serve the built React application
FROM node:16

# Set the working directory inside the container
WORKDIR /app

# Copy the built files from the previous stage
COPY --from=build /app/build ./build

# Install 'serve' to serve the static files
RUN npm install -g serve

# Expose the default React port
EXPOSE 8080

# Set the CMD to serve the build directory dynamically using the PORT environment variable
CMD ["serve", "-s", "-l", "8080", "./build"]