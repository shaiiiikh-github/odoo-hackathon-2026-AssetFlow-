import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import ProtectedRoute from "./ProtectedRoute";
import { appRoutes } from "./routeConfig";
import { ROUTE_PATHS } from "./routePaths";

export default function AppRoutes() {
  const publicRoutes = appRoutes.filter((route) => route.isPublic);
  const protectedRoutes = appRoutes.filter((route) => !route.isPublic);

  return (
    <BrowserRouter>
      <Routes>
        {publicRoutes.map(({ path, element: Element }) => (
          <Route key={path} path={path} element={<Element />} />
        ))}

        <Route element={<MainLayout />}>
          {protectedRoutes.map(({ path, element: Element, allowedRoles }) => (
            <Route
              key={path}
              path={path}
              element={
                <ProtectedRoute allowedRoles={allowedRoles}>
                  <Element />
                </ProtectedRoute>
              }
            />
          ))}
        </Route>

        <Route
          path="*"
          element={<Navigate to={ROUTE_PATHS.shared.notFound} replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}
