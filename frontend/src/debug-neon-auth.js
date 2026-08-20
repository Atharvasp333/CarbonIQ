/**
 * Neon Auth Token Debug Script
 * 
 * Run this in the browser console to check Neon Auth token structure
 */

import { authClient } from './lib/auth.js';

console.log('='.repeat(80));
console.log('NEON AUTH DEBUG');
console.log('='.repeat(80));

// 1. Check current session
console.log('\n[1] Checking Neon Auth Session...');
authClient.getSession().then(({ data, error }) => {
  if (error) {
    console.error('❌ Error getting session:', error);
    return;
  }
  
  console.log('\n✓ Session data structure:');
  console.log('Session keys:', Object.keys(data || {}));
  
  if (data?.session) {
    console.log('\n✓ Session object keys:', Object.keys(data.session));
    console.log('  - access_token:', data.session.access_token ? 'EXISTS' : 'MISSING');
    console.log('  - token_type:', data.session.token_type);
    console.log('  - expires_at:', data.session.expires_at);
    
    if (data.session.access_token) {
      const token = data.session.access_token;
      console.log('\n✓ Token details:');
      console.log('  - Length:', token.length);
      console.log('  - First 20 chars:', token.substring(0, 20) + '...');
      console.log('  - Last 20 chars:', '...' + token.substring(token.length - 20));
      
      // Try to decode JWT
      try {
        const parts = token.split('.');
        if (parts.length === 3) {
          const header = JSON.parse(atob(parts[0]));
          const payload = JSON.parse(atob(parts[1]));
          
          console.log('\n✓ JWT Header:', header);
          console.log('\n✓ JWT Payload:');
          console.log('  - Email:', payload.email || payload.sub);
          console.log('  - Issued at:', new Date(payload.iat * 1000).toISOString());
          console.log('  - Expires at:', new Date(payload.exp * 1000).toISOString());
          console.log('  - Is expired:', Date.now() / 1000 > payload.exp);
          console.log('  - Full payload:', payload);
        } else {
          console.warn('⚠️ Token is not a standard JWT (not 3 parts)');
          console.log('  Parts:', parts.length);
        }
      } catch (e) {
        console.warn('⚠️ Could not decode token as JWT:', e.message);
      }
    }
  } else {
    console.error('❌ No session object in data');
    console.log('Available data:', data);
  }
  
  if (data?.user) {
    console.log('\n✓ User object:');
    console.log('  - Email:', data.user.email);
    console.log('  - Name:', data.user.name);
    console.log('  - ID:', data.user.id);
  }
  
}).catch(err => {
  console.error('❌ Exception getting session:', err);
});

// 2. Check localStorage
console.log('\n[2] Checking localStorage...');
const authToken = localStorage.getItem('auth_token');
const neonJwt = localStorage.getItem('neon_jwt');

console.log('  - auth_token:', authToken ? 'EXISTS (' + authToken.length + ' chars)' : 'MISSING');
console.log('  - neon_jwt:', neonJwt ? 'EXISTS (' + neonJwt.length + ' chars)' : 'MISSING');

if (authToken) {
  console.log('\n  auth_token preview:', authToken.substring(0, 50) + '...');
}

// 3. Wait for async operation
console.log('\n' + '='.repeat(80));
console.log('Wait for async session check to complete...');
console.log('='.repeat(80));

export { authClient };
