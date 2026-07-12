import Charts from "../../components/dashboard/Charts";
import DashboardHeader from "../../components/dashboard/DashboardHeader";
import QuickActions from "../../components/dashboard/QuickActions";
import RecentActivity from "../../components/dashboard/RecentActivity";
import StatsGrid from "../../components/dashboard/StatsGrid";
import {
  assetStatusData,
  departmentDistributionData,
  managerKpis,
  quickActions,
  recentActivity,
} from "../../constants/managerDashboardData";

export default function ManagerDashboard() {
  return (
    <div className="space-y-6">
      <DashboardHeader />
      <StatsGrid items={managerKpis} />
      <Charts
        assetStatusData={assetStatusData}
        departmentDistributionData={departmentDistributionData}
      />

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <RecentActivity items={recentActivity} />
        <QuickActions items={quickActions} />
      </section>
    </div>
  );
}
