export const ROUTE_PATHS = {
  auth: {
    login: "/",
  },
  admin: {
    dashboard: "/admin",
    departments: "/admin/departments",
    categories: "/admin/categories",
    employees: "/admin/employees",
  },
  manager: {
    dashboard: "/manager",
    assets: "/manager/assets",
    registerAsset: "/manager/register-asset",
    allocation: "/manager/allocation",
    maintenance: "/manager/maintenance",
    reports: "/manager/reports",
  },
  employee: {
    dashboard: "/employee",
    myAssets: "/employee/my-assets",
    maintenanceRequest: "/employee/maintenance-request",
    returnRequest: "/employee/return-request",
    notifications: "/employee/notifications",
  },
  shared: {
    profile: "/shared/profile",
    notFound: "/shared/not-found",
  },
};
