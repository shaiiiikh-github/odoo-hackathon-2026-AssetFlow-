import { USER_ROLES } from "./roles";

export const demoUsers = [
  {
    email: "admin@assetflow.com",
    password: "Admin@123",
    role: USER_ROLES.admin,
    name: "Admin User",
    initials: "AU",
  },
  {
    email: "manager@assetflow.com",
    password: "Manager@123",
    role: USER_ROLES.assetManager,
    name: "Asset Manager",
    initials: "AM",
  },
  {
    email: "employee@assetflow.com",
    password: "Employee@123",
    role: USER_ROLES.employee,
    name: "Employee User",
    initials: "EU",
  },
];

export function getDemoUserByEmail(email) {
  return demoUsers.find(
    (user) => user.email.toLowerCase() === email.trim().toLowerCase(),
  );
}