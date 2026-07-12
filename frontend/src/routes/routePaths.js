export const ROUTE_PATHS = {
  auth: {
    login: "/",
  },
  admin: {
    dashboard: "/admin",
    departments: "/admin/departments",
    categories: "/admin/categories",
    employees: "/admin/employees",
    assetRequests: "/admin/asset-requests",
  },
  manager: {
    dashboard: "/manager",
    assets: "/manager/assets",
    registerAsset: "/manager/register-asset",
    allocation: "/manager/allocation",
    maintenance: "/manager/maintenance",
    reports: "/manager/reports",
    assetRequests: "/manager/asset-requests",
  },
  employee: {
    dashboard: "/employee",
    myAssets: "/employee/my-assets",
    assetRequests: "/employee/asset-requests",
    maintenanceRequest: "/employee/maintenance-request",
    returnRequest: "/employee/return-request",
    notifications: "/employee/notifications",
  },
  shared: {
    profile: "/shared/profile",
    notFound: "/shared/not-found",
  },
};
