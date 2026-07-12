import { Eye, ShieldCheck, XCircle } from "lucide-react";
import EmptyState from "../common/EmptyState";
import RequestStatusBadge from "./RequestStatusBadge";

export default function RequestTable({
  columns,
  rows,
  caption,
  emptyTitle,
  emptyDescription,
  onView,
  onApprove,
  onReject,
  readOnly = false,
}) {
  if (!rows.length) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="overflow-hidden rounded-[1.5rem] border border-white/80 bg-white shadow-[0_10px_30px_rgba(15,23,42,0.06)]">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-[#E2E8F0]">
          <caption className="sr-only">{caption}</caption>
          <thead className="bg-[#F8FAFC]">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="px-6 py-4 text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500"
                >
                  {column.label}
                </th>
              ))}
              {(onView || (!readOnly && (onApprove || onReject))) && (
                <th className="px-6 py-4 text-right text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {rows.map((row) => (
              <tr key={row.id} className="transition duration-200 hover:bg-blue-50/30">
                {columns.map((column) => (
                  <td key={column.key} className="whitespace-nowrap px-6 py-5 text-sm font-medium text-[#0F172A]">
                    {column.key === "status" ? (
                      <RequestStatusBadge status={row.status} />
                    ) : column.render ? (
                      column.render(row)
                    ) : (
                      row[column.key]
                    )}
                  </td>
                ))}
                {(onView || (!readOnly && (onApprove || onReject))) && (
                  <td className="whitespace-nowrap px-6 py-5 text-right">
                    <div className="inline-flex items-center gap-2">
                      {onView && (
                        <ActionButton label={`View ${row.id}`} onClick={() => onView(row)} icon={Eye} />
                      )}
                      {onApprove && (
                        <ActionButton label={`Approve ${row.id}`} onClick={() => onApprove(row)} icon={ShieldCheck} tone="success" />
                      )}
                      {onReject && (
                        <ActionButton label={`Reject ${row.id}`} onClick={() => onReject(row)} icon={XCircle} tone="danger" />
                      )}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ActionButton({ label, onClick, icon: Icon, tone = "neutral" }) {
  const toneClasses = {
    neutral: "border-[#E2E8F0] bg-white text-slate-600 hover:-translate-y-0.5 hover:bg-slate-50 hover:shadow-sm",
    success: "border-emerald-100 bg-white text-emerald-600 hover:-translate-y-0.5 hover:bg-emerald-50 hover:shadow-sm",
    danger: "border-rose-100 bg-white text-rose-600 hover:-translate-y-0.5 hover:bg-rose-50 hover:shadow-sm",
  };

  return (
    <button
      type="button"
      aria-label={label}
      className={`flex h-9 w-9 items-center justify-center rounded-xl border transition duration-200 focus-visible:outline-none focus-visible:ring-4 ${toneClasses[tone]}`}
      onClick={onClick}
    >
      <Icon size={16} />
    </button>
  );
}