# backend/ai-server/main.py

import json
from typing import Dict, Any, List

import os
import itertools

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import google.generativeai as genai

from mock_db import get_all_courses
from scheduler import generate_schedule

# -------------------------------------------------
# 1. 환경 변수 로드 & Gemini API 키 설정
# -------------------------------------------------
load_dotenv()

raw_keys = os.getenv("GEMINI_API_KEYS")
if raw_keys:
    GEMINI_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
else:
    # 예전 방식(GEMINI_API_KEY 하나만)도 호환
    single = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEYS = [single] if single.strip() else []

if not GEMINI_API_KEYS:
    raise RuntimeError(
        "Gemini API 키를 찾을 수 없습니다. .env 파일의 GEMINI_API_KEYS 또는 GEMINI_API_KEY를 확인하세요."
    )

# 라운드로빈으로 키를 돌려 쓰기 위한 iterator
_key_cycle = itertools.cycle(GEMINI_API_KEYS)


def get_gemini_model() -> genai.GenerativeModel:
    """
    여러 개의 Gemini API 키를 라운드로빈 방식으로 번갈아 사용해서
    GenerativeModel 인스턴스를 반환하는 헬퍼 함수.
    """
    api_key = next(_key_cycle)
    genai.configure(api_key=api_key)
    # 디버깅용 로그 (원하면 지워도 됨)
    print(f"[Gemini] Using API key prefix: {api_key[:8]}... (총 {len(GEMINI_API_KEYS)}개 중)")
    return genai.GenerativeModel("models/gemini-pro-latest")


# -------------------------------------------------
# 2. FastAPI 앱 설정
# -------------------------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 주소 허용 (배포 시에는 프론트엔드 도메인만 허용하는 게 안전)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# 3. 시간표 생성 API
# -------------------------------------------------
class ScheduleRequest(BaseModel):
    # 사용자가 선택한 과목 ID 리스트
    selected_course_ids: List[str]
    # 시간표 조건 (프론트엔드 변수명과 일치시킴)
    preferences: Dict[str, Any]


@app.post("/api/schedule")
def create_schedule_endpoint(request: ScheduleRequest):
    try:
        courses = get_all_courses()
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    # 사용자가 선택한 과목이 0개면 에러 처리
    if not request.selected_course_ids:
        raise HTTPException(status_code=400, detail="최소 1개 이상의 과목을 선택해주세요.")

    # 3가지 플랜 생성 (Seed를 다르게 주어서 변화를 줌)
    # Seed 10: 정석적인 추천 (Plan A)
    # Seed 20, 30: 약간의 랜덤성을 섞은 추천 (Plan B, C)
    plan_a = generate_schedule(courses, request.selected_course_ids, request.preferences, seed=10)
    plan_b = generate_schedule(courses, request.selected_course_ids, request.preferences, seed=20)
    plan_c = generate_schedule(courses, request.selected_course_ids, request.preferences, seed=30)

    # 결과가 하나라도 없으면 실패 메시지
    if not plan_a:
        return {
            "status": "fail",
            "message": "조건에 맞는 시간표를 생성할 수 없습니다. 학점 범위를 확인해주세요.",
        }

    return {
        "status": "success",
        "data": {
            "PLAN A": plan_a,
            "PLAN B": plan_b,
            "PLAN C": plan_c,
        },
    }


# -------------------------------------------------
# 4. AI 수업 추천 API
# -------------------------------------------------
class RecommendationRequest(BaseModel):
    major: str | None = None  # 학생 전공 (없어도 에러 안 나게)
    job_interest: str         # 희망 직무


@app.post("/recommend")
def recommand_courses(req: RecommendationRequest):
    try:
        # 1. mock_db.py에서 강의 데이터 직접 로딩
        all_courses = get_all_courses()

        # 2. AI에게 보낼 텍스트로 변환
        courses_text = "\n".join(
            [
                f"- {c['code']} {c['name']} ({c['department']}): "
                f"{c['time']} {','.join(c['day'])}"
                for c in all_courses
            ]
        )

        if req.major:
            student_intro = f"나는 {req.major} 전공 학생이고,"
        else:
            student_intro = "나는 컴퓨터 과학과 학생이고,"

        # 3. 프롬프트 작성 (JSON 형식을 강력하게 요구)
        prompt = f"""
        너는 대학교 수강신청 도우미 AI야.
        {student_intro} 희망 직무는 '{req.job_interest}'야.

        아래는 우리 학교에 개설된 강의 목록이야:
        {courses_text}

        이 중에서 내 희망 직무와 가장 관련성이 높고 도움이 될만한 강의 3~4개를 추천해줘.

        [중요] 반드시 아래와 같은 순수한 JSON 형식으로만 답변해.
        마크다운(```json)이나 다른 말은 절대 넣지 마.

        {{
            "recommended_codes": ["과목코드1", "과목코드2", "과목코드3"]
        }}
        """

        # 4. Gemini에게 질문하기 (요청마다 키를 라운드로빈으로 선택)
        model = get_gemini_model()
        response = model.generate_content(prompt)

        response_text = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(response_text)

        # 5. AI가 추천한 '코드'를 가지고, 실제 '강의 정보(객체)'를 찾아서 반환
        recommended_codes = result_json.get("recommended_codes", [])

        final_recommendations = [
            c for c in all_courses
            if c["code"] in recommended_codes
        ]

        return final_recommendations

    except Exception as e:
        print(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# 5. 개발용 로컬 실행
# -------------------------------------------------
if __name__ == "__main__":
    # uvicorn main:app --reload 와 동일
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
