import RequestStatusBadge from "./RequestStatusBadge";

export default function RequestTimeline({ items }) {
  return (
    <ol className="space-y-4">
      {items.map((item, index) => (
        <li key={`${item.status}-${item.timestamp}`} className="relative pl-8">
          {index !== items.length - 1 && (
            <span className="absolute left-[11px] top-6 h-full w-px bg-slate-200" />
          )}
          <span className="absolute left-0 top-1 flex h-6 w-6 items-center justify-center rounded-full bg-blue-50 text-[#2563EB] ring-4 ring-white">
            <span className="h-2.5 w-2.5 rounded-full bg-[#2563EB]" />
          </span>
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-[#0F172A]">{item.status}</p>
                <p className="mt-1 text-xs font-medium text-slate-500">{item.user}</p>
              </div>
              <RequestStatusBadge status={item.status} />
            </div>
            <p className="mt-3 text-sm font-medium leading-6 text-slate-600">{item.note}</p>
            <p className="mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
              {new Date(item.timestamp).toLocaleString()}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}