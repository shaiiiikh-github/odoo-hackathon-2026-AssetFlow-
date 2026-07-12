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
import ChartCard from "./ChartCard";
import StatusBadge from "./StatusBadge";

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-2xl border border-white/80 bg-white px-3 py-2 text-sm shadow-[0_12px_24px_rgba(15,23,42,0.12)]">
      <p className="font-semibold text-[#0F172A]">{label || payload[0].name}</p>
      <p className="font-medium text-slate-500">{payload[0].value} assets</p>
    </div>
  );
}

export default function Charts({ assetStatusData, departmentDistributionData }) {
  return (
    <section className="grid gap-6 xl:grid-cols-2">
      <ChartCard
        title="Asset Status"
        description="Current asset lifecycle mix"
        footer={
          <div className="grid gap-3 sm:grid-cols-3">
            {assetStatusData.map((item) => (
              <StatusBadge
                key={item.name}
                tone={item.tone}
                dotColor={item.color}
              >
                {item.name}
              </StatusBadge>
            ))}
          </div>
        }
      >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={assetStatusData}
                dataKey="value"
                nameKey="name"
                innerRadius={72}
                outerRadius={112}
                paddingAngle={4}
              >
                {assetStatusData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
            </PieChart>
          </ResponsiveContainer>
      </ChartCard>

      <ChartCard
        title="Department Distribution"
        description="Assets assigned across departments"
      >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={departmentDistributionData} barSize={28}>
              <CartesianGrid stroke="#E2E8F0" vertical={false} strokeDasharray="3 3" />
              <XAxis
                dataKey="department"
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
              <Bar dataKey="assets" fill="#2563EB" radius={[10, 10, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
      </ChartCard>
    </section>
  );
}
