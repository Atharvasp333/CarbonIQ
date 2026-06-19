import { createAuthClient } from '@neondatabase/neon-js/auth';

// Simple auth client — signIn, signUp, getSession, signOut
export const authClient = createAuthClient(import.meta.env.VITE_NEON_AUTH_URL);
