import { Bell, Menu, Search } from "lucide-react";

const defaultUser = {
  name: "Shabbir Ahmed",
  role: "Asset Manager",
  initials: "SA",
};

export default function TopNavbar({
  onOpenSidebar,
  user = defaultUser,
  searchPlaceholder = "Search assets, employees, requests...",
  notificationCount = 3,
}) {
  const hasNotifications = notificationCount > 0;

  return (
    <header className="sticky top-0 z-30 border-b border-[#E2E8F0] bg-white/95 backdrop-blur">
      <div className="flex h-16 items-center gap-3 px-4 sm:px-6 lg:px-8">
        <button
          type="button"
          aria-label="Open sidebar"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-[#E2E8F0] text-slate-600 transition-colors duration-200 hover:bg-slate-50 lg:hidden"
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
              className="h-11 w-full rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] pl-11 pr-4 text-sm font-medium text-[#1E293B] outline-none transition duration-200 placeholder:text-slate-400 focus:border-[#2563EB] focus:bg-white focus:ring-4 focus:ring-blue-100"
            />
          </label>
        </div>

        <button
          type="button"
          aria-label="Search"
          className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-[#E2E8F0] text-slate-600 transition-colors duration-200 hover:bg-slate-50 md:hidden"
        >
          <Search size={18} />
        </button>

        <div className="ml-auto flex items-center gap-2 sm:gap-3">
          <button
            type="button"
            aria-label="View notifications"
            className="relative inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-[#E2E8F0] text-slate-600 transition-colors duration-200 hover:bg-slate-50"
          >
            <Bell size={18} />
            {hasNotifications && (
              <span className="absolute right-2.5 top-2.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-[#EF4444]" />
            )}
          </button>

          <div className="flex min-w-0 items-center gap-3 rounded-2xl border border-[#E2E8F0] bg-white py-1.5 pl-1.5 pr-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#2563EB] text-sm font-semibold text-white">
              {user.initials}
            </div>

            <div className="hidden min-w-0 sm:block">
              <p className="truncate text-sm font-semibold leading-5 text-[#1E293B]">
                {user.name}
              </p>
              <p className="truncate text-xs font-medium leading-4 text-slate-500">
                {user.role}
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
