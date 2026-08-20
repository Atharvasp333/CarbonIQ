/**
 * Authentication Debug Script
 * Run this in the browser console to diagnose auth issues
 */

console.log('='.repeat(80));
console.log('AUTHENTICATION DEBUG');
console.log('='.repeat(80));

// 1. Check localStorage for token
const token = localStorage.getItem('auth_token');
console.log('\n[1] Token Storage:');
console.log('  Token exists:', !!token);
console.log('  Token length:', token ? token.length : 0);

if (token) {
  // Decode JWT (without verification)
  try {
    const parts = token.split('.');
    if (parts.length === 3) {
      const payload = JSON.parse(atob(parts[1]));
      console.log('  Token payload:');
      console.log('    - Email:', payload.email);
      console.log('    - User ID:', payload.sub);
      console.log('    - Expires:', new Date(payload.exp * 1000).toISOString());
      console.log('    - Is Expired:', Date.now() / 1000 > payload.exp);
    }
  } catch (e) {
    console.error('  Failed to decode token:', e.message);
  }
}

// 2. Check axios configuration
import api from './api/client.js';

console.log('\n[2] Axios Configuration:');
console.log('  BaseURL:', api.defaults.baseURL);
console.log('  Interceptors:', {
  request: api.interceptors.request.handlers.length,
  response: api.interceptors.response.handlers.length
});

// 3. Test profile endpoint (working)
console.log('\n[3] Testing Profile Endpoint (Expected: 200):');
api.get('/api/profile/')
  .then(res => {
    console.log('  ✓ SUCCESS:', res.status);
    console.log('  Response:', res.data);
  })
  .catch(err => {
    console.error('  ✗ FAILED:', err.response?.status, err.response?.data?.detail);
  });

// 4. Test intelligence endpoints (failing)
console.log('\n[4] Testing Intelligence Recommendations (Expected: 401 or 200):');
api.get('/api/intelligence/recommendations')
  .then(res => {
    console.log('  ✓ SUCCESS:', res.status);
    console.log('  Recommendations:', res.data?.recommendations?.length);
  })
  .catch(err => {
    console.error('  ✗ FAILED:', err.response?.status, err.response?.data?.detail);
    console.error('  Request headers:', err.config?.headers);
  });

console.log('\n[5] Testing Generate Insights (Expected: 401 or 200):');
api.post('/api/intelligence/generate-insights')
  .then(res => {
    console.log('  ✓ SUCCESS:', res.status);
  })
  .catch(err => {
    console.error('  ✗ FAILED:', err.response?.status, err.response?.data?.detail);
    console.error('  Request headers:', err.config?.headers);
  });

console.log('\n[6] Manual Request Test (with Authorization header):');
if (token) {
  fetch('http://localhost:8000/api/intelligence/recommendations', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  .then(res => {
    console.log('  Manual fetch status:', res.status);
    return res.json();
  })
  .then(data => {
    console.log('  Manual fetch data:', data);
  })
  .catch(err => {
    console.error('  Manual fetch error:', err);
  });
}

console.log('\n' + '='.repeat(80));
console.log('Wait for async requests to complete...');
console.log('='.repeat(80));
