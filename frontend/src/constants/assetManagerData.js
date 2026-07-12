import { CheckCircle2, Clock3, Laptop, PackageCheck, Users, Wrench } from "lucide-react";

export const assetSummary = [
  { label: "Total Assets", value: "1,284", change: "+24 this month", tone: "blue", icon: Laptop },
  { label: "Allocated", value: "932", change: "72.6% in use", tone: "emerald", icon: PackageCheck },
  { label: "Employees", value: "486", change: "Across 8 departments", tone: "amber", icon: Users },
  { label: "Maintenance", value: "38", change: "12 pending review", tone: "rose", icon: Wrench },
];

export const assetsSeed = [
  { id: "AST-2026-001", name: "MacBook Pro 14", category: "Laptop", department: "Engineering", assignee: "Anika Rao", status: "Allocated", condition: "Excellent" },
  { id: "AST-2026-002", name: "Dell Latitude 7440", category: "Laptop", department: "Operations", assignee: "Unassigned", status: "Available", condition: "Good" },
  { id: "AST-2026-003", name: "iPhone 15", category: "Mobile", department: "Sales", assignee: "Kabir Singh", status: "Allocated", condition: "Excellent" },
  { id: "AST-2026-004", name: "HP LaserJet Pro", category: "Printer", department: "Finance", assignee: "Unassigned", status: "Maintenance", condition: "Service Due" },
];

export const allocationSeed = [
  { id: "ALC-001", asset: "Dell Latitude 7440", employee: "Rohan Shah", department: "Operations", date: "12 Jul 2026", status: "Pending" },
  { id: "ALC-002", asset: "iPad Air", employee: "Meera Iyer", department: "Finance", date: "11 Jul 2026", status: "Allocated" },
  { id: "ALC-003", asset: "Monitor 27", employee: "Dev Malhotra", department: "Engineering", date: "10 Jul 2026", status: "Allocated" },
];

export const maintenanceSeed = [
  { id: "MNT-001", asset: "HP LaserJet Pro", requester: "Priya Menon", issue: "Paper feed failure", priority: "High", status: "Pending" },
  { id: "MNT-002", asset: "Dell Latitude 7440", requester: "Rohan Shah", issue: "Battery health low", priority: "Medium", status: "Approved" },
  { id: "MNT-003", asset: "iPhone 15", requester: "Kabir Singh", issue: "Screen protector replacement", priority: "Low", status: "Completed" },
];

export const reportStatusData = [
  { name: "Available", value: 314, color: "#22C55E", tone: "success" },
  { name: "Allocated", value: 932, color: "#2563EB", tone: "info" },
  { name: "Maintenance", value: 38, color: "#F59E0B", tone: "warning" },
];

export const monthlyAssetsData = [
  { month: "Feb", assets: 1020 },
  { month: "Mar", assets: 1088 },
  { month: "Apr", assets: 1136 },
  { month: "May", assets: 1184 },
  { month: "Jun", assets: 1240 },
  { month: "Jul", assets: 1284 },
];

export const requestStats = [
  { label: "Pending", value: "12", change: "Needs review", tone: "amber", icon: Clock3 },
  { label: "Approved", value: "18", change: "This week", tone: "blue", icon: CheckCircle2 },
  { label: "Completed", value: "44", change: "+9 this month", tone: "emerald", icon: PackageCheck },
  { label: "Urgent", value: "4", change: "High priority", tone: "rose", icon: Wrench },
];
