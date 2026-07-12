const toneClasses = {
  blue: "bg-blue-50 text-[#2563EB]",
  emerald: "bg-emerald-50 text-[#22C55E]",
  amber: "bg-amber-50 text-[#F59E0B]",
  rose: "bg-rose-50 text-[#EF4444]",
};

export default function StatCard({ label, value, change, icon: Icon, tone }) {
  return (
    <article className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-[#1E293B]">
            {value}
          </p>
        </div>
        {Icon && (
          <div
            className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl ${
              toneClasses[tone] || toneClasses.blue
            }`}
          >
            <Icon size={21} />
          </div>
        )}
      </div>
      {change && (
        <p className="mt-4 text-sm font-semibold text-slate-500">{change}</p>
      )}
    </article>
  );
}
