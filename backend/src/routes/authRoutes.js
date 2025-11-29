//라우터 연결

const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// POST http://localhost:3000/api/auth/signup
router.post('/signup', authController.register);

// POST http://localhost:3000/api/auth/login
router.post('/login', authController.login);

//POST hyttp://localhost:3000/api/auth/logout
router.post('/logout', authController.logout);

module.exports = router;