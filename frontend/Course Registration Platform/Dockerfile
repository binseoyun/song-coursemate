FROM node:20-alpine

WORKDIR /app

COPY package.json ./

# ★ 핵심: 기존 모듈 찌꺼기 없이 깨끗하게 설치
RUN npm install

COPY . .

EXPOSE 3000

# ★ 실행 명령어를 npx로 변경 (경로 문제 해결에 탁월함)
CMD ["npx", "vite", "--host"]