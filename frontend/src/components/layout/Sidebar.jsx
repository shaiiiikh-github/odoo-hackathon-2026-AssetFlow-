import { LogOut } from "lucide-react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { sidebarNavigation } from "../../constants/sidebarNavigation";
import { ROUTE_PATHS } from "../../routes/routePaths";
import useAuth from "../../hooks/useAuth";
import { getCurrentUser } from "../../utils/authMock";

export default function Sidebar({ isOpen = false, onClose }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { role, logout, user } = useAuth();
  const currentUser = user ?? getCurrentUser(location.pathname);
  const visibleItems = sidebarNavigation[role] ?? [];

  function handleLogout() {
    logout();
    onClose?.();
    navigate(ROUTE_PATHS.auth.login, { replace: true });
  }

  return (
    <>
      <button
        type="button"
        aria-label="Close sidebar"
        className={`fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-[2px] transition-opacity duration-200 lg:hidden ${
          isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
      />

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[280px] flex-col border-r border-white/70 bg-white/90 shadow-[12px_0_40px_rgba(15,23,42,0.06)] backdrop-blur-xl transition-transform duration-200 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-20 items-center border-b border-[#E2E8F0] px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] text-sm font-semibold text-white shadow-lg shadow-blue-500/20">
              AF
            </div>
            <div>
              <p className="text-base font-semibold tracking-tight text-[#0F172A]">AssetFlow Pro</p>
              <p className="text-xs font-medium text-slate-500">
                Smart Enterprise Asset Management
              </p>
            </div>
          </div>
        </div>

        <nav className="flex-1 space-y-7 overflow-y-auto px-4 py-5" aria-label="Primary">
          <div>
            <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
              {role === "admin"
                ? "Admin"
                : role === "asset-manager"
                  ? "Manager"
                  : "Employee"}
            </p>
            <div className="space-y-1">
              {visibleItems.map(({ label, to, icon: Icon }) => (
                <NavLink
                  key={`${label}-${to}`}
                  to={to}
                  end={to === "/admin" || to === "/manager" || to === "/employee"}
                  onClick={onClose}
                  className={({ isActive }) =>
                    `group relative flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-semibold transition duration-200 ${
                      isActive
                        ? "bg-gradient-to-r from-blue-50 to-indigo-50 text-[#2563EB] shadow-sm"
                        : "text-slate-600 hover:bg-slate-50 hover:text-[#0F172A]"
                    }`
                  }
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white text-current shadow-sm ring-1 ring-[#E2E8F0] group-hover:ring-blue-100">
                    <Icon size={17} />
                  </span>
                  <span>{label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        </nav>

        <div className="border-t border-[#E2E8F0] p-4">
          <div className="flex items-center gap-3 rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-3 shadow-sm">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] text-sm font-semibold text-white shadow-sm">
              {currentUser.initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-[#1E293B]">
                {currentUser.name}
              </p>
              <p className="truncate text-xs font-medium text-slate-500">
                {currentUser.role}
              </p>
            </div>
            <button
              type="button"
              aria-label="Logout"
              onClick={handleLogout}
              className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 hover:bg-white hover:text-rose-600"
            >
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
