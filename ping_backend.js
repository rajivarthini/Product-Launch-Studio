const fetch = require('node-fetch'); // wait, node 18+ has fetch natively

async function pingBackend() {
  try {
    const res = await fetch('http://127.0.0.1:8001/docs');
    console.log('Backend Status:', res.status);
  } catch(e) {
    console.error('Backend Ping Error:', e.message);
  }
}

pingBackend();
