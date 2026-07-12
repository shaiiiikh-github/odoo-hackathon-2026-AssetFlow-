import { Laptop } from "lucide-react";
import StatusBadge from "../dashboard/StatusBadge";

const statusTone = {
  Available: "success",
  Allocated: "info",
  Maintenance: "warning",
};

export default function AssetCard({ asset }) {
  return (
    <article className="rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-[#2563EB]">
            <Laptop size={21} />
          </span>
          <div>
            <h3 className="text-sm font-semibold text-[#1E293B]">{asset.name}</h3>
            <p className="mt-1 text-xs font-semibold text-slate-500">{asset.id}</p>
          </div>
        </div>
        <StatusBadge tone={statusTone[asset.status] || "neutral"}>{asset.status}</StatusBadge>
      </div>

      <dl className="mt-5 grid grid-cols-2 gap-4 text-sm">
        <div>
          <dt className="font-semibold text-slate-400">Category</dt>
          <dd className="mt-1 font-semibold text-[#1E293B]">{asset.category}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-400">Department</dt>
          <dd className="mt-1 font-semibold text-[#1E293B]">{asset.department}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-400">Assignee</dt>
          <dd className="mt-1 font-semibold text-[#1E293B]">{asset.assignee}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-400">Condition</dt>
          <dd className="mt-1 font-semibold text-[#1E293B]">{asset.condition}</dd>
        </div>
      </dl>
    </article>
  );
}
