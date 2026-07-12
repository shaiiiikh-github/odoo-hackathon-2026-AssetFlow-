import { Navigate } from "react-router-dom";
import { ROUTE_PATHS } from "./routePaths";
import { getCurrentRole } from "../utils/authMock";

export default function ProtectedRoute({ allowedRoles, children }) {
  const currentRole = getCurrentRole();
  const canAccessRoute = allowedRoles.includes(currentRole);

  if (!canAccessRoute) {
    return <Navigate to={ROUTE_PATHS.shared.notFound} replace />;
  }

  return children;
}
