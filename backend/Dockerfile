FROM node:18-alpine AS base

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY . .

ENV NODE_ENV=production
EXPOSE 8000

CMD ["node", "src/app.js"]

