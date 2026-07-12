import { Navigate } from "react-router-dom";
import { ROUTE_PATHS } from "./routePaths";
import useAuth from "../hooks/useAuth";

export default function ProtectedRoute({ allowedRoles, children }) {
  const { isAuthenticated, role } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to={ROUTE_PATHS.auth.login} replace />;
  }

  if (!allowedRoles.includes(role)) {
    return <Navigate to={ROUTE_PATHS.auth.login} replace />;
  }

  return children;
}
