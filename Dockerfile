FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
# create writable dirs and set ownership to node user
RUN mkdir -p /app/data /app/logs && chown -R node:node /app
ENV NODE_ENV=production PORT=8080
USER node
EXPOSE 8080
CMD ["node", "main.js"]
