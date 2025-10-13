const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000';

app.use(express.static(path.join(__dirname, 'public')));

app.get('/config.js', (_req, res) => {
  res.type('application/javascript').send(`window.__BACKEND_URL__ = '${BACKEND_URL}';`);
});

app.get('/', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend listening on http://localhost:${PORT}`);
});