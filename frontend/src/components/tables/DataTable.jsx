import { Pencil, Trash2 } from "lucide-react";
import EmptyState from "../common/EmptyState";
import StatusBadge from "../dashboard/StatusBadge";
import { getStatusTone } from "../../constants/statusTones";

export default function DataTable({
  columns,
  rows,
  onEdit,
  onDelete,
  caption = "Data table",
  emptyTitle,
  emptyDescription,
}) {
  const hasActions = Boolean(onEdit || onDelete);

  if (!rows.length) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-[#E2E8F0]">
          <caption className="sr-only">{caption}</caption>
          <thead className="bg-[#F8FAFC]">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
                >
                  {column.label}
                </th>
              ))}
              {hasActions && (
                <th className="px-5 py-4 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {rows.map((row) => (
              <tr
                key={row.id}
                className="transition duration-200 hover:bg-slate-50"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className="whitespace-nowrap px-5 py-4 text-sm font-medium text-[#1E293B]"
                  >
                    {column.key === "status" ? (
                      <StatusBadge tone={getStatusTone(row.status)}>
                        {row.status}
                      </StatusBadge>
                    ) : (
                      column.render ? column.render(row) : row[column.key]
                    )}
                  </td>
                ))}
                {hasActions && (
                  <td className="whitespace-nowrap px-5 py-4 text-right">
                    <div className="inline-flex items-center gap-2">
                      {onEdit && (
                        <button
                          type="button"
                          aria-label={`Edit ${row.id}`}
                          className="flex h-9 w-9 items-center justify-center rounded-xl border border-[#E2E8F0] text-slate-600 transition duration-200 hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-slate-200"
                          onClick={() => onEdit(row)}
                        >
                          <Pencil size={16} />
                        </button>
                      )}
                      {onDelete && (
                        <button
                          type="button"
                          aria-label={`Delete ${row.id}`}
                          className="flex h-9 w-9 items-center justify-center rounded-xl border border-red-100 text-[#EF4444] transition duration-200 hover:bg-red-50 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-red-100"
                          onClick={() => onDelete(row)}
                        >
                          <Trash2 size={16} />
                        </button>
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
