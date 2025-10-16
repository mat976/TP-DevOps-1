const express = require('express');
const path = require('path');
// LiveReload (dev uniquement)
const useLiveReload = process.env.LIVE_RELOAD === 'true';
let lrServer = null;
const app = express();
if (useLiveReload) {
  try {
    const livereload = require('livereload');
    lrServer = livereload.createServer({ exts: ['html', 'css', 'js'] });
    lrServer.watch(path.join(__dirname, 'public'));
  } catch (e) {
    console.warn('LiveReload non disponible. Installez "livereload" et "connect-livereload" en dev.');
  }
}
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Désactiver cache navigateur pour les assets statiques
if (useLiveReload) {
  try {
    const connectLivereload = require('connect-livereload');
    app.use(connectLivereload());
  } catch { }
}
app.use(express.static(path.join(__dirname, 'public'), { etag: false, maxAge: 0 }));

app.get('/config.js', (_req, res) => {
  res.set('Cache-Control', 'no-store');
  res.type('application/javascript').send(`window.__BACKEND_URL__ = '${BACKEND_URL}';`);
});

app.get('/', (_req, res) => {
  res.set('Cache-Control', 'no-store');
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Route pour la page Casino
app.get('/casino', (_req, res) => {
  res.set('Cache-Control', 'no-store');
  res.sendFile(path.join(__dirname, 'public', 'casino.html'));
});

// Alias direct si on appelle /casino.html
app.get('/casino.html', (_req, res) => {
  res.set('Cache-Control', 'no-store');
  res.sendFile(path.join(__dirname, 'public', 'casino.html'));
});

app.listen(PORT, () => {
  console.log(`Frontend listening on http://localhost:${PORT}`);
  if (lrServer) {
    console.log('LiveReload actif sur les fichiers du dossier public.');
  }
});