import Charts from "../../components/dashboard/Charts";
import DashboardHeader from "../../components/dashboard/DashboardHeader";
import RequestCard from "../../components/assetRequests/RequestCard";
import QuickActions from "../../components/dashboard/QuickActions";
import RecentActivity from "../../components/dashboard/RecentActivity";
import SectionCard from "../../components/dashboard/SectionCard";
import StatsGrid from "../../components/dashboard/StatsGrid";
import {
  assetStatusData,
  departmentDistributionData,
  managerKpis,
  quickActions,
  recentActivity,
} from "../../constants/managerDashboardData";
import { AlertCircle, ClipboardList, ShieldCheck } from "lucide-react";
import useAuth from "../../hooks/useAuth";
import useAssetRequests from "../../hooks/useAssetRequests";

export default function ManagerDashboard() {
  const { user, role } = useAuth();
  const requestApi = useAssetRequests();
  const summary = requestApi.getManagerRequestSummary();
  const requestStats = [
    {
      label: "Pending Requests",
      value: String(summary.pending),
      change: "Need action",
      tone: "amber",
      icon: ClipboardList,
    },
    {
      label: "Approved Today",
      value: String(summary.approvedToday),
      change: "Allocated successfully",
      tone: "emerald",
      icon: ShieldCheck,
    },
    {
      label: "Rejected Today",
      value: String(summary.rejectedToday),
      change: "Rejected with notes",
      tone: "rose",
      icon: AlertCircle,
    },
    {
      label: "Average Approval Time",
      value: summary.averageApprovalTime,
      change: "Workflow efficiency",
      tone: "blue",
      icon: ClipboardList,
    },
  ];
  const recentRequests = requestApi.getVisibleRequests(role, user.email).slice(0, 3);

  return (
    <div className="space-y-6">
      <DashboardHeader />
      <StatsGrid items={managerKpis} />
      <StatsGrid items={requestStats} />
      <Charts
        assetStatusData={assetStatusData}
        departmentDistributionData={departmentDistributionData}
      />

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <RecentActivity items={recentActivity} />
        <QuickActions items={quickActions} />
      </section>

      <SectionCard title="Recent Asset Requests" description="Incoming request queue">
        <div className="grid gap-4 md:grid-cols-3">
          {recentRequests.map((request) => (
            <RequestCard key={request.id} request={request} to="/manager/asset-requests" />
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
