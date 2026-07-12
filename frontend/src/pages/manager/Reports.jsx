import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import ChartCard from "../../components/dashboard/ChartCard";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import StatsGrid from "../../components/dashboard/StatsGrid";
import StatusBadge from "../../components/dashboard/StatusBadge";
import {
  assetSummary,
  monthlyAssetsData,
  reportStatusData,
} from "../../constants/assetManagerData";

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-xl border border-[#E2E8F0] bg-white px-3 py-2 text-sm shadow-lg">
      <p className="font-semibold text-[#1E293B]">{label || payload[0].name}</p>
      <p className="font-medium text-slate-500">{payload[0].value} assets</p>
    </div>
  );
}

export default function Reports() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Asset Manager"
        title="Reports"
        description="Analyze asset availability, allocation growth, and maintenance impact."
      />

      <StatsGrid items={assetSummary} />

      <section className="grid gap-6 xl:grid-cols-2">
        <ChartCard
          title="Asset Status"
          description="Portfolio status split"
          footer={
            <div className="grid gap-3 sm:grid-cols-3">
              {reportStatusData.map((item) => (
                <StatusBadge key={item.name} tone={item.tone} dotColor={item.color}>
                  {item.name}
                </StatusBadge>
              ))}
            </div>
          }
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={reportStatusData}
                dataKey="value"
                nameKey="name"
                innerRadius={72}
                outerRadius={112}
                paddingAngle={4}
              >
                {reportStatusData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Asset Growth" description="Registered assets by month">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyAssetsData} barSize={34}>
              <CartesianGrid stroke="#E2E8F0" vertical={false} />
              <XAxis
                dataKey="month"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748B", fontSize: 12, fontWeight: 600 }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748B", fontSize: 12, fontWeight: 600 }}
              />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="assets" fill="#2563EB" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </section>

      <SectionCard title="Report Notes" description="Operational summary">
        <div className="grid gap-4 md:grid-cols-3">
          <ReportNote title="Utilization" value="72.6%" />
          <ReportNote title="Available Pool" value="314 assets" />
          <ReportNote title="Maintenance Load" value="38 assets" />
        </div>
      </SectionCard>
    </div>
  );
}

function ReportNote({ title, value }) {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4">
      <p className="text-sm font-semibold text-slate-500">{title}</p>
      <p className="mt-2 text-xl font-semibold text-[#1E293B]">{value}</p>
    </div>
  );
}
