import {
  ClipboardCheck,
  Laptop,
  PieChart,
  Plus,
  ShieldCheck,
  Users,
  Wrench,
} from "lucide-react";

export const managerKpis = [
  {
    label: "Total Assets",
    value: "1,284",
    change: "+12.4%",
    tone: "blue",
    icon: Laptop,
  },
  {
    label: "Employees",
    value: "486",
    change: "+8 new",
    tone: "emerald",
    icon: Users,
  },
  {
    label: "Allocated",
    value: "932",
    change: "72.6%",
    tone: "amber",
    icon: ClipboardCheck,
  },
  {
    label: "Maintenance",
    value: "38",
    change: "-6 this week",
    tone: "rose",
    icon: Wrench,
  },
];

export const assetStatusData = [
  { name: "Available", value: 314, color: "#22C55E", tone: "success" },
  { name: "Allocated", value: 932, color: "#2563EB", tone: "info" },
  { name: "Maintenance", value: 38, color: "#F59E0B", tone: "warning" },
];

export const departmentDistributionData = [
  { department: "Engineering", assets: 342 },
  { department: "Finance", assets: 164 },
  { department: "HR", assets: 96 },
  { department: "Operations", assets: 278 },
  { department: "Sales", assets: 224 },
  { department: "Support", assets: 180 },
];

export const recentActivity = [
  {
    title: "MacBook Pro allocated",
    description: "Assigned to Neha Kapoor in Engineering",
    time: "12 min ago",
  },
  {
    title: "Maintenance approved",
    description: "Dell Latitude keyboard replacement request",
    time: "42 min ago",
  },
  {
    title: "New asset registered",
    description: "HP LaserJet Pro added to Operations",
    time: "2 hr ago",
  },
  {
    title: "Return request received",
    description: "iPhone 15 return requested by Arjun Mehta",
    time: "Yesterday",
  },
];

export const quickActions = [
  {
    title: "Register Asset",
    description: "Add a new company asset",
    icon: Plus,
    to: "/manager/register-asset",
  },
  {
    title: "Allocate Asset",
    description: "Assign assets to employees",
    icon: ShieldCheck,
    to: "/manager/allocation",
  },
  {
    title: "Maintenance",
    description: "Review service requests",
    icon: Wrench,
    to: "/manager/maintenance",
  },
  {
    title: "Reports",
    description: "View asset insights",
    icon: PieChart,
    to: "/manager/reports",
  },
];
