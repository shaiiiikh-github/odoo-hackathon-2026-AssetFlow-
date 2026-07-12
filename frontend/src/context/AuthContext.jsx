import { createContext, useMemo, useState } from "react";
import { USER_ROLES } from "../constants/roles";
import { demoUsers, getDemoUserByEmail } from "../constants/authUsers";
import {
  clearAuthSession,
  readAuthSession,
  writeAuthSession,
} from "../utils/authSession";

const AuthContext = createContext(undefined);

function normalizeUser(user) {
  if (!user) {
    return null;
  }

  return {
    name: user.name,
    email: user.email,
    role: user.role,
    initials: user.initials,
  };
}

function createAuthStateFromSession(session) {
  const user = normalizeUser(session.user);

  return {
    user,
    role: session.role ?? user?.role ?? null,
    isAuthenticated: Boolean(user && (session.role ?? user?.role)),
    rememberMe: Boolean(session.rememberMe),
  };
}

function validateDemoCredentials({ email, password }) {
  const matchedUser = getDemoUserByEmail(email);

  if (!matchedUser || matchedUser.password !== password) {
    return {
      success: false,
      message:
        "Invalid email or password. Please verify your credentials or use one of the demo accounts below.",
    };
  }

  return {
    success: true,
    user: normalizeUser(matchedUser),
    role: matchedUser.role,
  };
}

export function AuthProvider({ children }) {
  const [authState, setAuthState] = useState(() =>
    createAuthStateFromSession(readAuthSession()),
  );

  async function login(credentials) {
    const result = validateDemoCredentials(credentials);

    if (!result.success) {
      return result;
    }

    const nextUser = result.user;
    const nextRole = result.role;

    writeAuthSession(nextUser, nextRole, Boolean(credentials.rememberMe));
    setAuthState({
      user: nextUser,
      role: nextRole,
      isAuthenticated: true,
      rememberMe: Boolean(credentials.rememberMe),
    });

    return result;
  }

  function logout() {
    clearAuthSession();
    setAuthState({
      user: null,
      role: null,
      isAuthenticated: false,
      rememberMe: false,
    });
  }

  const value = useMemo(
    () => ({
      login,
      logout,
      user: authState.user,
      role: authState.role,
      isAuthenticated: authState.isAuthenticated,
      rememberMe: authState.rememberMe,
      demoUsers,
      roles: USER_ROLES,
    }),
    [authState],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export { AuthContext };