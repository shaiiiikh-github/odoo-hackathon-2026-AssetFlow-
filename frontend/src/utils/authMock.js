import { USER_ROLES } from "../constants/roles";
import { readAuthSession } from "./authSession";

export const roleLabels = {
  [USER_ROLES.admin]: "Admin",
  [USER_ROLES.assetManager]: "Asset Manager",
  [USER_ROLES.employee]: "Employee",
};

export function getRoleFromPath(pathname) {
  if (pathname.startsWith("/manager")) {
    return USER_ROLES.assetManager;
  }

  if (pathname.startsWith("/employee")) {
    return USER_ROLES.employee;
  }

  return USER_ROLES.admin;
}

export function getCurrentRole(pathname = window.location.pathname) {
  const sessionRole = readAuthSession().role;

  return sessionRole || getRoleFromPath(pathname);
}

export function getCurrentUser(pathname) {
  const session = readAuthSession();
  const role = session.role || getCurrentRole(pathname);

  if (session.user) {
    return {
      ...session.user,
      role: roleLabels[role] || session.user.role,
    };
  }

  return {
    name: role === USER_ROLES.admin ? "Shabbir Ahmed" : "Shabbir Ahmed",
    role: roleLabels[role],
    initials: "SA",
  };
}
