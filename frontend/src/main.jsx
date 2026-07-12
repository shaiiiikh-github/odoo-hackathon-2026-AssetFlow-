import React from "react";
import ReactDOM from "react-dom/client";

import { AuthProvider } from "./context/AuthContext";
import { AssetRequestProvider } from "./context/AssetRequestContext";
import AppRoutes from "./routes/AppRoutes";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <AssetRequestProvider>
        <AppRoutes />
      </AssetRequestProvider>
    </AuthProvider>
  </React.StrictMode>
);
