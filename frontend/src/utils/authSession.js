const AUTH_USER_KEY = "assetflow:auth-user";
const AUTH_ROLE_KEY = "assetflow:user-role";
const AUTH_REMEMBER_KEY = "assetflow:auth-remember-me";

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function getStorageBucket(rememberMe) {
  if (!canUseStorage()) {
    return null;
  }

  return rememberMe ? window.localStorage : window.sessionStorage;
}

function safeParse(value) {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

export function readAuthSession() {
  if (!canUseStorage()) {
    return { user: null, role: null, rememberMe: false };
  }

  const localUser = safeParse(window.localStorage.getItem(AUTH_USER_KEY));
  const localRole = window.localStorage.getItem(AUTH_ROLE_KEY);
  const localRememberMe = window.localStorage.getItem(AUTH_REMEMBER_KEY) === "true";
  const sessionUser = safeParse(window.sessionStorage.getItem(AUTH_USER_KEY));
  const sessionRole = window.sessionStorage.getItem(AUTH_ROLE_KEY);

  if (localUser && localRole) {
    return { user: localUser, role: localRole, rememberMe: localRememberMe };
  }

  if (sessionUser && sessionRole) {
    return { user: sessionUser, role: sessionRole, rememberMe: false };
  }

  return { user: null, role: null, rememberMe: false };
}

export function writeAuthSession(user, role, rememberMe = false) {
  if (!canUseStorage()) {
    return;
  }

  const preferredStorage = getStorageBucket(rememberMe);
  const secondaryStorage = rememberMe ? window.sessionStorage : window.localStorage;

  secondaryStorage.removeItem(AUTH_USER_KEY);
  secondaryStorage.removeItem(AUTH_ROLE_KEY);
  secondaryStorage.removeItem(AUTH_REMEMBER_KEY);

  preferredStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  preferredStorage.setItem(AUTH_ROLE_KEY, role);

  if (rememberMe) {
    preferredStorage.setItem(AUTH_REMEMBER_KEY, "true");
    window.sessionStorage.removeItem(AUTH_USER_KEY);
    window.sessionStorage.removeItem(AUTH_ROLE_KEY);
    window.sessionStorage.removeItem(AUTH_REMEMBER_KEY);
    return;
  }

  window.localStorage.removeItem(AUTH_USER_KEY);
  window.localStorage.removeItem(AUTH_ROLE_KEY);
  window.localStorage.removeItem(AUTH_REMEMBER_KEY);
  preferredStorage.setItem(AUTH_REMEMBER_KEY, "false");
}

export function clearAuthSession() {
  if (!canUseStorage()) {
    return;
  }

  window.localStorage.removeItem(AUTH_USER_KEY);
  window.localStorage.removeItem(AUTH_ROLE_KEY);
  window.localStorage.removeItem(AUTH_REMEMBER_KEY);
  window.sessionStorage.removeItem(AUTH_USER_KEY);
  window.sessionStorage.removeItem(AUTH_ROLE_KEY);
  window.sessionStorage.removeItem(AUTH_REMEMBER_KEY);
}

export function getStoredRole() {
  if (!canUseStorage()) {
    return null;
  }

  return window.localStorage.getItem(AUTH_ROLE_KEY);
}

export function getStoredUser() {
  return readAuthSession().user;
}
