export const employees = [
  {
    id: "EMP-1001",
    name: "Emily Carter",
    email: "employee@assetflow.com",
    department: "Finance",
    role: "employee",
    initials: "EC",
  },
  {
    id: "EMP-1002",
    name: "Marcus Reed",
    email: "manager@assetflow.com",
    department: "Operations",
    role: "asset-manager",
    initials: "MR",
  },
  {
    id: "EMP-1003",
    name: "Olivia Grant",
    email: "admin@assetflow.com",
    department: "IT Governance",
    role: "admin",
    initials: "OG",
  },
  {
    id: "EMP-1004",
    name: "Neha Kapoor",
    email: "neha.kapoor@assetflow.com",
    department: "Engineering",
    role: "employee",
    initials: "NK",
  },
  {
    id: "EMP-1005",
    name: "Arjun Mehta",
    email: "arjun.mehta@assetflow.com",
    department: "Sales",
    role: "employee",
    initials: "AM",
  },
];

export function getEmployeeByEmail(email) {
  return employees.find(
    (employee) => employee.email.toLowerCase() === email.trim().toLowerCase(),
  );
}