import {
  BarChart3,
  Building2,
  ClipboardList,
  Gauge,
  Laptop,
  FileText,
  Users,
  UserRound,
  Wrench,
} from "lucide-react";
import { USER_ROLES } from "./roles";

export const sidebarNavigation = {
  [USER_ROLES.admin]: [
    { label: "Dashboard", to: "/admin", icon: Gauge },
    { label: "Departments", to: "/admin/departments", icon: Building2 },
    { label: "Employees", to: "/admin/employees", icon: Users },
    { label: "Categories", to: "/admin/categories", icon: BarChart3 },
    { label: "Asset Requests", to: "/admin/asset-requests", icon: FileText },
  ],
  [USER_ROLES.assetManager]: [
    { label: "Dashboard", to: "/manager", icon: Gauge },
    { label: "Assets", to: "/manager/assets", icon: Laptop },
    { label: "Allocation", to: "/manager/allocation", icon: ClipboardList },
    { label: "Asset Requests", to: "/manager/asset-requests", icon: FileText },
    { label: "Maintenance", to: "/manager/maintenance", icon: Wrench },
    { label: "Reports", to: "/manager/reports", icon: BarChart3 },
  ],
  [USER_ROLES.employee]: [
    { label: "Dashboard", to: "/employee", icon: Gauge },
    { label: "My Assets", to: "/employee/my-assets", icon: Laptop },
    { label: "Asset Requests", to: "/employee/asset-requests", icon: FileText },
    { label: "Maintenance Request", to: "/employee/maintenance-request", icon: Wrench },
    { label: "Return Request", to: "/employee/return-request", icon: ClipboardList },
    { label: "Profile", to: "/shared/profile", icon: UserRound },
  ],
};
