FROM node:20 AS build

WORKDIR /app

# 1. 패키지 정보만 먼저 복사
COPY package*.json ./

# 2. devDependencies까지 포함해서 설치 (vite 강제 설치)
RUN npm install --include=dev

# 3. 나머지 소스 복사
COPY . .

# 4. 빌드 (package.json의 "build": "vite build" 실행)
RUN npm run build

# 5. Nginx로 정적 파일 서비스
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
