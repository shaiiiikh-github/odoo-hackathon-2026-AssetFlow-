import {
  BarChart3,
  Bell,
  Building2,
  ClipboardList,
  Gauge,
  Laptop,
  Layers3,
  Settings,
  UserRound,
  Users,
  Wrench,
} from "lucide-react";
import { USER_ROLES } from "./roles";

export const sidebarNavigation = [
  {
    label: "MAIN",
    items: [
      { label: "Dashboard", to: "/admin", icon: Gauge, roles: [USER_ROLES.admin] },
      { label: "Dashboard", to: "/manager", icon: Gauge, roles: [USER_ROLES.assetManager] },
      { label: "Dashboard", to: "/employee", icon: Gauge, roles: [USER_ROLES.employee] },
      { label: "Assets", to: "/manager/assets", icon: Laptop, roles: [USER_ROLES.assetManager] },
      { label: "My Assets", to: "/employee/my-assets", icon: Laptop, roles: [USER_ROLES.employee] },
      { label: "Notifications", to: "/employee/notifications", icon: Bell, roles: [USER_ROLES.employee] },
      { label: "Allocation", to: "/manager/allocation", icon: ClipboardList, roles: [USER_ROLES.assetManager] },
    ],
  },
  {
    label: "OPERATIONS",
    items: [
      { label: "Maintenance", to: "/manager/maintenance", icon: Wrench, roles: [USER_ROLES.assetManager] },
      { label: "Maintenance Request", to: "/employee/maintenance-request", icon: Wrench, roles: [USER_ROLES.employee] },
      { label: "Return Request", to: "/employee/return-request", icon: ClipboardList, roles: [USER_ROLES.employee] },
      { label: "Reports", to: "/manager/reports", icon: BarChart3, roles: [USER_ROLES.assetManager] },
    ],
  },
  {
    label: "ADMIN",
    items: [
      { label: "Employees", to: "/admin/employees", icon: Users, roles: [USER_ROLES.admin] },
      { label: "Departments", to: "/admin/departments", icon: Building2, roles: [USER_ROLES.admin] },
      { label: "Categories", to: "/admin/categories", icon: Layers3, roles: [USER_ROLES.admin] },
      { label: "Profile", to: "/shared/profile", icon: UserRound, roles: [USER_ROLES.admin, USER_ROLES.assetManager, USER_ROLES.employee] },
      { label: "Settings", to: "/admin", icon: Settings, roles: [USER_ROLES.admin] },
    ],
  },
];
