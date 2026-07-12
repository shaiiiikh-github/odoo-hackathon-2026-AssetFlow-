import { Bell, ChevronDown, LogOut, Menu, Search, UserRound } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ROUTE_PATHS } from "../../routes/routePaths";
import useAuth from "../../hooks/useAuth";
import useAssetRequests from "../../hooks/useAssetRequests";

const defaultUser = {
  name: "Shabbir Ahmed",
  role: "Asset Manager",
  initials: "SA",
};

export default function TopNavbar({
  onOpenSidebar,
  user = defaultUser,
  searchPlaceholder = "Search assets, employees, requests...",
  notificationCount,
}) {
  const navigate = useNavigate();
  const { user: authUser, logout } = useAuth();
  const requestApi = useAssetRequests();
  const [isProfileMenuOpen, setIsProfileMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const activeUser = authUser ?? user;
  const derivedNotificationCount = requestApi.getUnreadNotificationCount(
    activeUser?.role,
    activeUser?.email,
  );
  const displayNotificationCount =
    typeof notificationCount === "number" ? notificationCount : derivedNotificationCount;
  const hasNotifications = displayNotificationCount > 0;

  useEffect(() => {
    function handleOutsideClick(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsProfileMenuOpen(false);
      }
    }

    function handleEscape(event) {
      if (event.key === "Escape") {
        setIsProfileMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  function handleLogout() {
    logout();
    setIsProfileMenuOpen(false);
    navigate(ROUTE_PATHS.auth.login, { replace: true });
  }

  return (
    <header className="sticky top-0 z-30 border-b border-white/70 bg-white/85 backdrop-blur-xl shadow-[0_1px_0_rgba(15,23,42,0.04)]">
      <div className="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
        <button
          type="button"
          aria-label="Open sidebar"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-[#E2E8F0] bg-white text-slate-600 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-100 hover:text-[#2563EB] hover:shadow-md lg:hidden"
          onClick={onOpenSidebar}
        >
          <Menu size={20} />
        </button>

        <div className="hidden min-w-0 flex-1 md:block">
          <label className="relative block max-w-xl">
            <span className="sr-only">Search</span>
            <Search
              size={18}
              className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              type="search"
              placeholder={searchPlaceholder}
              className="h-11 w-full rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] pl-11 pr-4 text-sm font-medium text-[#0F172A] outline-none shadow-sm transition placeholder:text-slate-400 focus:border-[#2563EB] focus:bg-white focus:ring-4 focus:ring-blue-100"
            />
          </label>
        </div>

        <button
          type="button"
          aria-label="Search"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-[#E2E8F0] bg-white text-slate-600 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-100 hover:text-[#2563EB] hover:shadow-md md:hidden"
        >
          <Search size={18} />
        </button>

        <div className="ml-auto flex items-center gap-2 sm:gap-3">
          <button
            type="button"
            aria-label="View notifications"
            className="relative inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-[#E2E8F0] bg-white text-slate-600 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-100 hover:text-[#2563EB] hover:shadow-md"
          >
            <Bell size={18} />
            {hasNotifications && (
              <span className="absolute right-2.5 top-2.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-[#EF4444]" />
            )}
          </button>

          <div className="relative" ref={menuRef}>
            <button
              type="button"
              onClick={() => setIsProfileMenuOpen((value) => !value)}
              className="flex min-w-0 items-center gap-3 rounded-2xl border border-[#E2E8F0] bg-white py-1.5 pl-1.5 pr-3 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-100 hover:shadow-md"
              aria-haspopup="menu"
              aria-expanded={isProfileMenuOpen}
            >
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] text-sm font-semibold text-white shadow-sm">
                {activeUser.initials}
              </div>

              <div className="hidden min-w-0 sm:block text-left">
                <p className="truncate text-sm font-semibold leading-5 text-[#1E293B]">
                  {activeUser.name}
                </p>
                <p className="truncate text-xs font-medium leading-4 text-slate-500">
                  {activeUser.role}
                </p>
              </div>

              <ChevronDown size={16} className="hidden text-slate-400 sm:block" />
            </button>

            <div
              className={`absolute right-0 top-[calc(100%+0.75rem)] w-72 origin-top-right rounded-2xl border border-white/80 bg-white p-2 shadow-[0_18px_40px_rgba(15,23,42,0.12)] backdrop-blur-xl transition duration-150 ${
                isProfileMenuOpen
                  ? "pointer-events-auto scale-100 opacity-100"
                  : "pointer-events-none scale-95 opacity-0"
              }`}
              role="menu"
            >
              <div className="rounded-xl bg-slate-50 px-4 py-3 ring-1 ring-slate-100">
                <p className="text-sm font-semibold text-slate-900">{activeUser.name}</p>
                <p className="text-xs font-medium text-slate-500">{activeUser.role}</p>
              </div>

              <button
                type="button"
                className="mt-2 flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm font-medium text-slate-700 transition hover:bg-slate-50 hover:text-[#0F172A]"
              >
                <UserRound size={16} className="text-slate-400" />
                Profile
              </button>

              <button
                type="button"
                onClick={handleLogout}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left text-sm font-medium text-rose-600 transition hover:bg-rose-50"
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
