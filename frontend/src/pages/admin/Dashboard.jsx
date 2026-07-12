import ActivityCard from "../../components/dashboard/ActivityCard";
import PageHeader from "../../components/dashboard/PageHeader";
import QuickActionCard from "../../components/dashboard/QuickActionCard";
import SectionCard from "../../components/dashboard/SectionCard";
import StatsGrid from "../../components/dashboard/StatsGrid";
import {
  adminActivity,
  adminStats,
  categoriesSeed,
  departmentsSeed,
  employeesSeed,
} from "../../constants/adminData";
import { quickActions } from "../../constants/managerDashboardData";

const adminActions = [
  { ...quickActions[0], title: "Departments", description: "Create departments", to: "/admin/departments" },
  { ...quickActions[1], title: "Categories", description: "Manage asset categories", to: "/admin/categories" },
  { ...quickActions[2], title: "Employees", description: "Create and promote users", to: "/admin/employees" },
];

export default function AdminDashboard() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Admin Dashboard"
        title="Welcome Back"
        description="Manage organization structure, employee access, and asset master data from a single admin workspace."
      />

      <StatsGrid items={adminStats} />

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <SectionCard title="Master Data Health" description="Current admin setup">
          <div className="grid gap-4 sm:grid-cols-3">
            <Summary label="Departments" value={departmentsSeed.length} />
            <Summary label="Categories" value={categoriesSeed.length} />
            <Summary label="Employees" value={employeesSeed.length} />
          </div>
        </SectionCard>

        <SectionCard title="Admin Actions" description="Common setup tasks">
          <div className="grid gap-3">
            {adminActions.map((item) => (
              <QuickActionCard key={item.title} {...item} />
            ))}
          </div>
        </SectionCard>
      </section>

      <SectionCard title="Recent Admin Activity" description="Latest configuration changes">
        <ol className="space-y-5">
          {adminActivity.map((item, index) => (
            <ActivityCard
              key={item.title}
              {...item}
              index={index}
              isLast={index === adminActivity.length - 1}
            />
          ))}
        </ol>
      </SectionCard>
    </div>
  );
}

function Summary({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4">
      <p className="text-sm font-semibold text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-[#1E293B]">{value}</p>
    </div>
  );
}
