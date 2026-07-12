import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import TopNavbar from "../components/layout/TopNavbar";
import { getCurrentUser } from "../utils/authMock";

export default function MainLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();
  const currentUser = getCurrentUser(location.pathname);

  const openSidebar = () => setIsSidebarOpen(true);
  const closeSidebar = () => setIsSidebarOpen(false);

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#F8FAFC_0%,#F8FAFC_52%,#EEF2FF_100%)] text-[#0F172A]">
      <div className="flex min-h-screen">
        <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

        <div className="flex min-w-0 flex-1 flex-col lg:pl-[280px]">
          <TopNavbar onOpenSidebar={openSidebar} user={currentUser} />

          <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
            <div className="mx-auto w-full max-w-7xl animate-[soft-fade-up_180ms_ease-out]">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
