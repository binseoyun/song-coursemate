# 1. Base Image
FROM node:18-alpine

# 2. 작업 디렉토리 설정
WORKDIR /usr/src/app

# 3. 의존성 설치 (캐시 활용을 위해 package.json 먼저 복사)
COPY package*.json ./
RUN npm install

# 4. 소스 코드 복사
COPY . .

# 5. 포트 노출 (Node.js 서버 포트)
EXPOSE 8000

# 6. 실행 명령어
CMD ["node", "src/app.js"]