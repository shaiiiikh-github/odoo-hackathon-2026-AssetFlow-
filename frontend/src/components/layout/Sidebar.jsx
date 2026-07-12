import { LogOut } from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { sidebarNavigation } from "../../constants/sidebarNavigation";
import { getCurrentRole, getCurrentUser } from "../../utils/authMock";

export default function Sidebar({ isOpen = false, onClose }) {
  const location = useLocation();
  const currentRole = getCurrentRole(location.pathname);
  const currentUser = getCurrentUser(location.pathname);

  const visibleSections = sidebarNavigation
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => item.roles.includes(currentRole)),
    }))
    .filter((section) => section.items.length > 0);

  return (
    <>
      <button
        type="button"
        aria-label="Close sidebar"
        className={`fixed inset-0 z-40 bg-slate-950/30 transition-opacity lg:hidden ${
          isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
      />

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[280px] flex-col border-r border-[#E2E8F0] bg-white transition-transform duration-200 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center border-b border-[#E2E8F0] px-6">
          <div>
            <p className="text-lg font-semibold text-[#2563EB]">AssetFlow Pro</p>
            <p className="text-xs font-medium text-slate-500">
              Smart Enterprise Asset Management
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-7 overflow-y-auto px-4 py-5" aria-label="Primary">
          {visibleSections.map((section) => (
            <div key={section.label}>
              <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
                {section.label}
              </p>
              <div className="space-y-1">
                {section.items.map(({ label, to, icon: Icon }) => (
                  <NavLink
                    key={`${label}-${to}`}
                    to={to}
                    end={to === "/admin" || to === "/manager" || to === "/employee"}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-semibold transition duration-200 ${
                        isActive
                          ? "bg-blue-50 text-[#2563EB]"
                          : "text-slate-600 hover:bg-slate-50 hover:text-[#1E293B]"
                      }`
                    }
                  >
                    <Icon size={18} />
                    <span>{label}</span>
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-[#E2E8F0] p-4">
          <div className="flex items-center gap-3 rounded-2xl bg-[#F8FAFC] p-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#2563EB] text-sm font-semibold text-white">
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
              className="flex h-9 w-9 items-center justify-center rounded-xl text-slate-500 hover:bg-white"
            >
              <LogOut size={17} />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
