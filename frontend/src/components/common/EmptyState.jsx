import { Inbox } from "lucide-react";

export default function EmptyState({
  title = "No records found",
  description = "Records will appear here once data is available.",
  icon: Icon = Inbox,
  action,
}) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center rounded-[1.5rem] border border-dashed border-[#D7E1EE] bg-gradient-to-b from-white to-slate-50 p-8 text-center shadow-sm">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-slate-400 shadow-sm ring-1 ring-slate-100">
        <Icon size={22} />
      </span>
      <h3 className="mt-4 text-sm font-semibold text-[#0F172A]">{title}</h3>
      <p className="mt-2 max-w-sm text-sm font-medium leading-6 text-slate-500">
        {description}
      </p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
