const fs = require('fs');
const path = require('path');

// Write a dummy image for testing
const dummyImage = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
  'base64'
);
fs.writeFileSync('test_image.png', dummyImage);

async function testUpload() {
  const formData = new FormData();
  formData.append('product_image', new Blob([dummyImage], { type: 'image/png' }), 'test_image.png');
  formData.append('height', '10');
  formData.append('width', '10');
  formData.append('weight', '500');
  formData.append('description', 'Test Description');
  formData.append('platform', 'amazon');

  console.log('Sending request to frontend proxy...');
  try {
    const res = await fetch('http://localhost:3000/api/workflow', {
      method: 'POST',
      body: formData,
    });
    
    console.log(`Status: ${res.status}`);
    const text = await res.text();
    console.log(`Response: ${text.substring(0, 1000)}`);
  } catch (err) {
    console.error('Fetch error:', err);
  }
}

testUpload();
