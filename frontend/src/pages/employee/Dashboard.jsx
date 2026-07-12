import { Link } from "react-router-dom";
import { AlertCircle, Clock3, RotateCcw, ShieldCheck } from "lucide-react";
import RequestCard from "../../components/assetRequests/RequestCard";
import EmployeeAssetCard from "../../components/employee/EmployeeAssetCard";
import NotificationPanel from "../../components/employee/NotificationPanel";
import PageHeader from "../../components/dashboard/PageHeader";
import QuickActionCard from "../../components/dashboard/QuickActionCard";
import SectionCard from "../../components/dashboard/SectionCard";
import StatsGrid from "../../components/dashboard/StatsGrid";
import { quickActions } from "../../constants/managerDashboardData";
import useAuth from "../../hooks/useAuth";
import useAssetRequests from "../../hooks/useAssetRequests";

const employeeActions = [
  {
    ...quickActions[2],
    title: "Maintenance Request",
    description: "Raise an issue",
    to: "/employee/maintenance-request",
  },
  {
    ...quickActions[1],
    title: "Return Request",
    description: "Request asset return",
    to: "/employee/return-request",
  },
];

export default function EmployeeDashboard() {
  const { user, role } = useAuth();
  const requestApi = useAssetRequests();
  const assignedAssets = requestApi.getEmployeeAssets(user.email);
  const summary = requestApi.getEmployeeRequestSummary(user.email);
  const notifications = requestApi.getNotificationsForUser(role, user.email);
  const recentRequests = requestApi.getVisibleRequests(role, user.email).slice(0, 3);

  const employeeStats = [
    {
      label: "Pending Requests",
      value: String(summary.pending),
      change: "Awaiting review",
      tone: "amber",
      icon: Clock3,
    },
    {
      label: "Approved Requests",
      value: String(summary.approved),
      change: "Allocated assets",
      tone: "emerald",
      icon: ShieldCheck,
    },
    {
      label: "Rejected Requests",
      value: String(summary.rejected),
      change: "Needs follow-up",
      tone: "rose",
      icon: AlertCircle,
    },
    {
      label: "Latest Status",
      value: summary.latestStatus,
      change: "Most recent request",
      tone: "blue",
      icon: RotateCcw,
    },
  ];

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
            {assignedAssets.slice(0, 2).map((asset) => (
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

      <SectionCard title="Recent Requests" description="Latest request statuses">
        <div className="grid gap-4 md:grid-cols-3">
          {recentRequests.map((request) => (
            <RequestCard
              key={request.id}
              request={request}
              to="/employee/asset-requests"
            />
          ))}
        </div>
      </SectionCard>

      <NotificationPanel notifications={notifications.slice(0, 3)} />
    </div>
  );
}
