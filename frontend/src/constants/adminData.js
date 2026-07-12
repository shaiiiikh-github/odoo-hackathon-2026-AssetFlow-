import { Building2, Layers3, UserCog, Users } from "lucide-react";

export const adminStats = [
  { label: "Departments", value: "8", change: "+2 this quarter", tone: "blue", icon: Building2 },
  { label: "Categories", value: "14", change: "6 active groups", tone: "emerald", icon: Layers3 },
  { label: "Employees", value: "486", change: "+18 this month", tone: "amber", icon: Users },
  { label: "Asset Managers", value: "12", change: "Across 5 teams", tone: "rose", icon: UserCog },
];

export const departmentsSeed = [
  { id: "DEP-001", name: "Engineering", head: "Neha Kapoor", employees: 142, status: "Active" },
  { id: "DEP-002", name: "Operations", head: "Rohan Shah", employees: 96, status: "Active" },
  { id: "DEP-003", name: "Finance", head: "Priya Menon", employees: 48, status: "Active" },
  { id: "DEP-004", name: "People Ops", head: "Aman Verma", employees: 34, status: "Active" },
];

export const categoriesSeed = [
  { id: "CAT-001", name: "Laptops", code: "LAP", assets: 428, status: "Active" },
  { id: "CAT-002", name: "Mobile Devices", code: "MOB", assets: 214, status: "Active" },
  { id: "CAT-003", name: "Networking", code: "NET", assets: 86, status: "Active" },
  { id: "CAT-004", name: "Office Equipment", code: "OFF", assets: 156, status: "Active" },
];

export const employeesSeed = [
  { id: "EMP-001", name: "Anika Rao", email: "anika@assetflow.test", department: "Engineering", role: "Employee", status: "Active" },
  { id: "EMP-002", name: "Kabir Singh", email: "kabir@assetflow.test", department: "Operations", role: "Asset Manager", status: "Active" },
  { id: "EMP-003", name: "Meera Iyer", email: "meera@assetflow.test", department: "Finance", role: "Employee", status: "Active" },
  { id: "EMP-004", name: "Dev Malhotra", email: "dev@assetflow.test", department: "Engineering", role: "Employee", status: "Inactive" },
];

export const adminActivity = [
  { title: "Department created", description: "Facilities was added by Admin", time: "18 min ago" },
  { title: "Employee promoted", description: "Kabir Singh is now an Asset Manager", time: "1 hr ago" },
  { title: "Category updated", description: "Networking warranty rules were revised", time: "Today" },
];
