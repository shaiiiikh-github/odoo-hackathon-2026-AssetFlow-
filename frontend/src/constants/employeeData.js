import { Bell, Laptop, RotateCcw, ShieldCheck, Wrench } from "lucide-react";

export const employeeStats = [
  { label: "My Assets", value: "4", change: "2 critical devices", tone: "blue", icon: Laptop },
  { label: "Active Requests", value: "2", change: "Awaiting review", tone: "amber", icon: Wrench },
  { label: "Returns", value: "1", change: "Pending pickup", tone: "emerald", icon: RotateCcw },
  { label: "Notifications", value: "5", change: "3 unread", tone: "rose", icon: Bell },
];

export const employeeAssets = [
  { id: "AST-2026-001", name: "MacBook Pro 14", category: "Laptop", assignedDate: "04 Jun 2026", condition: "Excellent", status: "Allocated" },
  { id: "AST-2026-014", name: "Magic Keyboard", category: "Accessory", assignedDate: "04 Jun 2026", condition: "Good", status: "Allocated" },
  { id: "AST-2026-020", name: "Dell Monitor 27", category: "Display", assignedDate: "18 May 2026", condition: "Good", status: "Allocated" },
  { id: "AST-2026-087", name: "iPhone 15", category: "Mobile", assignedDate: "12 Apr 2026", condition: "Excellent", status: "Allocated" },
];

export const employeeRequests = [
  { id: "REQ-001", asset: "MacBook Pro 14", type: "Maintenance", issue: "Battery drains quickly", status: "Pending" },
  { id: "REQ-002", asset: "Magic Keyboard", type: "Return", issue: "No longer needed", status: "Approved" },
];

export const employeeNotifications = [
  { id: "NOT-001", title: "Asset allocated", message: "MacBook Pro 14 was assigned to you.", time: "Today", status: "Unread", icon: ShieldCheck },
  { id: "NOT-002", title: "Maintenance pending", message: "Your battery request is awaiting manager review.", time: "Yesterday", status: "Unread", icon: Wrench },
  { id: "NOT-003", title: "Return approved", message: "Magic Keyboard return request has been approved.", time: "10 Jul 2026", status: "Read", icon: RotateCcw },
  { id: "NOT-004", title: "Policy reminder", message: "Keep assigned devices updated and encrypted.", time: "08 Jul 2026", status: "Read", icon: Bell },
];
