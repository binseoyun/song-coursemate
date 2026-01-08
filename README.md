#숙명여대 수강신청 도우미 
숙명여자대학교 컴퓨터과학과 학생들을 위한 마이크로서비스 기반(MSA) 수강신청 및 과목 추천 플랫폼입니다. Docker와 Kubernetes(Kind) 환경에서 구동되며, AI 기반 과목 추천 기능을 제공합니다.

🛠 Tech Stack
Frontend: React, Vite

Backend: Node.js, Express

AI Server: Python, FastAPI, Gemini API

Database: MySQL 8.0

Infrastructure: Docker, Kubernetes (Kind)

⚙️ 환경 설정 (필수)
프로젝트 실행 전, 환경 변수 설정이 필요합니다.

프로젝트 루트 경로에 .env.docker 파일을 생성합니다.

env.docker.example 파일의 내용을 복사하여 붙여넣고, 특히 GEMINI_API_KEY 값을 채워주세요.



# 예시
GEMINI_API_KEY=your_google_gemini_api_key_here
🚀 실행 방법 1: Docker Compose (간편 실행)
가장 빠르게 개발 환경을 구축하고 실행하는 방법입니다.

1. 빌드 및 실행
Bash

docker compose --env-file .env.docker up --build
2. 접속 정보
Frontend: http://localhost:3000

Backend API: http://localhost:8000

AI Server: http://localhost:5000

MySQL: localhost:3306

☸️ 실행 방법 2: Kubernetes with Kind (운영 환경 시뮬레이션)
실제 운영 환경과 유사한 Kubernetes 클러스터(Kind) 환경에서 실행하는 방법입니다. (Windows PowerShell 기준)

1단계: 프로젝트 폴더 이동
PowerShell

cd "Cloudsystem/Course Registration Platform"
2단계: 도커 이미지 빌드 (Image Build)
쿠버네티스에 배포할 4개의 이미지를 빌드합니다.



# 1. 데이터베이스 (경로 확인 필수)
docker build -t my-database:v1 ./database

# 2. 백엔드
docker build -t my-backend:v1 ./backend

# 3. AI 서버
docker build -t my-ai-server:v1 ./backend/ai-server

# 4. 프론트엔드
docker build -t my-frontend:v1 "./frontend/Course Registration Platform"
3단계: Kind 클러스터 생성
Control-plane과 Worker 노드가 포함된 클러스터를 생성합니다.



# 1. 클러스터 설정 파일 생성 (multi-node-config.yaml)
@'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
'@ | Set-Content -Encoding UTF8 multi-node-config.yaml

# 2. 기존 클러스터 삭제 (충돌 방지) 및 생성
kind delete cluster --name my-cluster
kind create cluster --name my-cluster --config multi-node-config.yaml
4단계: 이미지를 클러스터로 로드 (Kind Load)
[중요] 로컬에서 빌드한 이미지를 Kind 클러스터 내부로 밀어 넣어야 ErrImagePull 에러가 발생하지 않습니다.



kind load docker-image my-database:v1 --name my-cluster
kind load docker-image my-backend:v1 --name my-cluster
kind load docker-image my-ai-server:v1 --name my-cluster
kind load docker-image my-frontend:v1 --name my-cluster
5단계: 쿠버네티스 배포 (Deploy)
PowerShell

kubectl apply -f k8s/
6단계: 상태 확인 및 초기 데이터 주입
서버가 완전히 실행된 후, 로그인을 위한 초기 데이터를 주입합니다.



# 1. 모든 파드가 'Running' 상태인지 확인
kubectl get pods -n sugang-system -w

# 2. 백엔드 파드 이름 변수 저장 및 데이터 주입 (PowerShell)
$POD_NAME = (kubectl get pods -n sugang-system -l app=backend -o jsonpath="{.items[0].metadata.name}")
kubectl exec -it $POD_NAME -n sugang-system -- node src/seedData.js
성공 시 "데이터가 성공적으로 추가되었습니다" 메시지가 출력됩니다.

7단계: 외부 접속 허용 (Port-Forwarding)
각 서비스를 로컬 브라우저에서 접속하기 위해 새로운 터미널 창을 각각 열어서 실행하세요. (터미널을 끄면 연결이 끊깁니다.)

Terminal A (Frontend): http://localhost:3000


kubectl port-forward svc/frontend-service 3000:3000 -n sugang-system
Terminal B (Backend): http://localhost:8000



kubectl port-forward svc/backend-service 8000:8000 -n sugang-system
Terminal C (AI Server): http://localhost:5000



kubectl port-forward svc/ai-server-service 5000:5000 -n sugang-system

#프로젝트 전체 구조는 아래 pdf에 자세히 기술되어있습니다.
[song-coursemate.pdf](https://github.com/user-attachments/files/24499380/song-coursemate.pdf)


