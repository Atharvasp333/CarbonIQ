import { createInternalNeonAuth } from '@neondatabase/neon-js/auth';

const _internal = createInternalNeonAuth(import.meta.env.VITE_NEON_AUTH_URL, {
  fetchOptions: { credentials: 'include' },
});

// The Better Auth client instance (signIn, signUp, getSession, signOut, etc.)
export const authClient = _internal.adapter.getBetterAuthInstance
  ? _internal.adapter.getBetterAuthInstance()
  : _internal.adapter;

/**
 * Get JWT for the current session.
 * Strategy:
 *  1. Try getJWTToken() from the internal client (works if cookie is accessible)
 *  2. Fall back to localStorage cache (set at login/signup time via set-auth-jwt header)
 */
export async function getJwtToken() {
  // Try live token first
  try {
    const token = await _internal.getJWTToken();
    if (token) {
      localStorage.setItem('neon_jwt', token); // keep cache fresh
      return token;
    }
  } catch { /* ignore */ }

  // Fall back to cached token
  const cached = localStorage.getItem('neon_jwt');
  return cached ?? null;
}
