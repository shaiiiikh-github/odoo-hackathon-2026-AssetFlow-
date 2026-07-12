export default function ActivityCard({ title, description, time, index, isLast }) {
  return (
    <li className="relative flex gap-4">
      <div className="flex flex-col items-center">
        <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-blue-50 text-sm font-semibold text-[#2563EB] ring-1 ring-blue-100">
          {index + 1}
        </span>
        {!isLast && <span className="mt-2 h-full w-px flex-1 bg-[#E2E8F0]" />}
      </div>

      <div className="min-w-0 pb-1">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <h3 className="text-sm font-semibold text-[#0F172A]">{title}</h3>
          <span className="text-xs font-semibold text-slate-400">{time}</span>
        </div>
        <p className="mt-1 text-sm font-medium leading-6 text-slate-500">
          {description}
        </p>
      </div>
    </li>
  );
}
