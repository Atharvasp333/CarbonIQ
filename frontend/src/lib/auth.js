import { createInternalNeonAuth } from '@neondatabase/neon-js/auth';
import { BetterAuthReactAdapter } from '@neondatabase/neon-js/auth/react/adapters';

export const _neonAuth = createInternalNeonAuth(import.meta.env.VITE_NEON_AUTH_URL, {
  adapter: BetterAuthReactAdapter(),
  fetchOptions: { credentials: 'include' },
});

// React-aware client — has useSession, signIn, signUp, getSession, signOut
export const authClient = _neonAuth.adapter;

// Get JWT for the current session (for backend API calls)
export async function getJwtToken() {
  try {
    const token = await _neonAuth.getJWTToken();
    if (token) {
      localStorage.setItem('neon_jwt', token);
      return token;
    }
  } catch { /* ignore */ }
  return localStorage.getItem('neon_jwt') ?? null;
}
