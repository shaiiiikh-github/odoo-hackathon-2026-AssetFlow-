import { Link } from "react-router-dom";
import EmployeeAssetCard from "../../components/employee/EmployeeAssetCard";
import NotificationPanel from "../../components/employee/NotificationPanel";
import PageHeader from "../../components/dashboard/PageHeader";
import QuickActionCard from "../../components/dashboard/QuickActionCard";
import SectionCard from "../../components/dashboard/SectionCard";
import StatsGrid from "../../components/dashboard/StatsGrid";
import {
  employeeAssets,
  employeeNotifications,
  employeeStats,
} from "../../constants/employeeData";
import { quickActions } from "../../constants/managerDashboardData";

const employeeActions = [
  { ...quickActions[2], title: "Maintenance Request", description: "Raise an issue", to: "/employee/maintenance-request" },
  { ...quickActions[1], title: "Return Request", description: "Request asset return", to: "/employee/return-request" },
];

export default function EmployeeDashboard() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Employee Dashboard"
        title="Welcome Back"
        description="Track assigned assets, request maintenance, submit returns, and stay updated on asset activity."
      />

      <StatsGrid items={employeeStats} />

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <SectionCard
          title="Assigned Assets"
          description="Your primary active assets"
          action={
            <Link
              to="/employee/my-assets"
              className="text-sm font-semibold text-[#2563EB] hover:text-blue-700"
            >
              View all
            </Link>
          }
        >
          <div className="grid gap-4 md:grid-cols-2">
            {employeeAssets.slice(0, 2).map((asset) => (
              <EmployeeAssetCard key={asset.id} asset={asset} />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Quick Actions" description="Common employee workflows">
          <div className="grid gap-3">
            {employeeActions.map((action) => (
              <QuickActionCard key={action.title} {...action} />
            ))}
          </div>
        </SectionCard>
      </section>

      <NotificationPanel notifications={employeeNotifications.slice(0, 3)} />
    </div>
  );
}
