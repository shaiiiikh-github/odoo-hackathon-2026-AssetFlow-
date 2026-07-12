import { USER_ROLES } from "../constants/roles";

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
  return localStorage.getItem("assetflow:user-role") || getRoleFromPath(pathname);
}

export function getCurrentUser(pathname) {
  const role = getCurrentRole(pathname);

  return {
    name: role === USER_ROLES.admin ? "Shabbir Ahmed" : "Shabbir Ahmed",
    role: roleLabels[role],
    initials: "SA",
  };
}
