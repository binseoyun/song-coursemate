# 1. Base Image
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사
COPY . .

# 5. 포트 노출 (FastAPI 포트)
EXPOSE 5000

# 6. 실행 명령어 (외부 접속 허용 0.0.0.0 필수!)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]