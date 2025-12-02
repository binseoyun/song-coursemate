// backend/src/app.js
const express = require('express');
const cors = require('cors');
const sequelize = require('./config/database');
const User = require('./models/User');
const authRoutes = require('./routes/authRoutes');
require('dotenv').config();

const app = express();

//ai 관련
const aiRoutes=require('./routes/aiRoutes')
app.use('/api/ai',aiRoutes);



// CORS 설정 (프론트 주소)
app.use(cors({
  origin: 'http://localhost:3000',
}));

app.use(express.json());

// /api/auth → authRoutes
app.use('/api/auth', authRoutes);

// 404 처리
app.use((req, res, next) => {
  console.log(`[404 에러] 경로를 찾을 수 없음: ${req.url}`);
  res.status(404).json({ message: `페이지를 찾을 수 없습니다: ${req.url}` });
});

// ✅ 포트 8000으로 고정 (환경변수에 PORT가 있어도 8000 쓰고 싶으면 그냥 8000 상수로)
const PORT = 8000;

// DB 동기화 후 서버 실행
sequelize.sync({ force: false })
  .then(() => {
    console.log('데이터베이스 연결 및 테이블 생성 완료!');
    app.listen(PORT, () => {
      console.log(`서버 실행 중! PORT: ${PORT}`);
    });
  })
  .catch((err) => {
    console.error('DB 연결 실패:', err);
  });
