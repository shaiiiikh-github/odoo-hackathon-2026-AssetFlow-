import Login from "../pages/auth/Login";
import AdminDashboard from "../pages/admin/Dashboard";
import Categories from "../pages/admin/Categories";
import Departments from "../pages/admin/Departments";
import Employees from "../pages/admin/Employees";
import ManagerDashboard from "../pages/manager/Dashboard";
import Assets from "../pages/manager/Assets";
import Allocation from "../pages/manager/Allocation";
import Maintenance from "../pages/manager/Maintenance";
import RegisterAsset from "../pages/manager/RegisterAsset";
import Reports from "../pages/manager/Reports";
import EmployeeDashboard from "../pages/employee/Dashboard";
import MaintenanceRequest from "../pages/employee/MaintenanceRequest";
import MyAssets from "../pages/employee/MyAssets";
import Notifications from "../pages/employee/Notifications";
import ReturnRequest from "../pages/employee/ReturnRequest";
import NotFound from "../pages/shared/NotFound";
import Profile from "../pages/shared/Profile";
import { USER_ROLES } from "../constants/roles";
import { ROUTE_PATHS } from "./routePaths";

const adminOnly = [USER_ROLES.admin];
const managerOnly = [USER_ROLES.assetManager];
const employeeOnly = [USER_ROLES.employee];
const authenticatedUsers = [
  USER_ROLES.admin,
  USER_ROLES.assetManager,
  USER_ROLES.employee,
];

export const defaultAuthenticatedPath = {
  [USER_ROLES.admin]: ROUTE_PATHS.admin.dashboard,
  [USER_ROLES.assetManager]: ROUTE_PATHS.manager.dashboard,
  [USER_ROLES.employee]: ROUTE_PATHS.employee.dashboard,
};

export const appRoutes = [
  {
    path: ROUTE_PATHS.auth.login,
    element: Login,
    isPublic: true,
  },
  {
    path: ROUTE_PATHS.admin.dashboard,
    element: AdminDashboard,
    allowedRoles: adminOnly,
  },
  {
    path: ROUTE_PATHS.admin.departments,
    element: Departments,
    allowedRoles: adminOnly,
  },
  {
    path: ROUTE_PATHS.admin.categories,
    element: Categories,
    allowedRoles: adminOnly,
  },
  {
    path: ROUTE_PATHS.admin.employees,
    element: Employees,
    allowedRoles: adminOnly,
  },
  {
    path: ROUTE_PATHS.manager.dashboard,
    element: ManagerDashboard,
    allowedRoles: managerOnly,
  },
  {
    path: ROUTE_PATHS.manager.assets,
    element: Assets,
    allowedRoles: managerOnly,
  },
  {
    path: ROUTE_PATHS.manager.registerAsset,
    element: RegisterAsset,
    allowedRoles: managerOnly,
  },
  {
    path: ROUTE_PATHS.manager.allocation,
    element: Allocation,
    allowedRoles: managerOnly,
  },
  {
    path: ROUTE_PATHS.manager.maintenance,
    element: Maintenance,
    allowedRoles: managerOnly,
  },
  {
    path: ROUTE_PATHS.manager.reports,
    element: Reports,
    allowedRoles: managerOnly,
  },
  {
    path: ROUTE_PATHS.employee.dashboard,
    element: EmployeeDashboard,
    allowedRoles: employeeOnly,
  },
  {
    path: ROUTE_PATHS.employee.myAssets,
    element: MyAssets,
    allowedRoles: employeeOnly,
  },
  {
    path: ROUTE_PATHS.employee.maintenanceRequest,
    element: MaintenanceRequest,
    allowedRoles: employeeOnly,
  },
  {
    path: ROUTE_PATHS.employee.returnRequest,
    element: ReturnRequest,
    allowedRoles: employeeOnly,
  },
  {
    path: ROUTE_PATHS.employee.notifications,
    element: Notifications,
    allowedRoles: employeeOnly,
  },
  {
    path: ROUTE_PATHS.shared.profile,
    element: Profile,
    allowedRoles: authenticatedUsers,
  },
  {
    path: ROUTE_PATHS.shared.notFound,
    element: NotFound,
    allowedRoles: authenticatedUsers,
  },
];
