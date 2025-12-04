# 1. MySQL 8.0 공식 이미지 사용
FROM mysql:8.0

# 2. (선택사항) 한글 설정 파일 복사
# 만약 conf.d/my.cnf 파일을 만들었다면 아래 주석 해제
COPY ./conf.d/my.cnf /etc/mysql/conf.d/my.cnf

# 3. 초기화 SQL 스크립트 복사 (테이블 생성 등)
COPY ./init.sql /docker-entrypoint-initdb.d/