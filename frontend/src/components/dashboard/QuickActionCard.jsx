import { Link } from "react-router-dom";

export default function QuickActionCard({ title, description, icon: Icon, to }) {
  return (
    <Link
      to={to}
      className="group rounded-[1.5rem] border border-[#E2E8F0] bg-white p-4 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-[#2563EB] hover:shadow-[0_12px_24px_rgba(37,99,235,0.08)]"
    >
      <div className="flex items-start gap-3">
        {Icon && (
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-[#2563EB] transition duration-200 group-hover:bg-[#2563EB] group-hover:text-white">
            <Icon size={19} />
          </span>
        )}
        <span className="min-w-0">
          <span className="block text-sm font-semibold text-[#0F172A]">
            {title}
          </span>
          <span className="mt-1 block text-sm font-medium leading-5 text-slate-500">
            {description}
          </span>
        </span>
      </div>
    </Link>
  );
}
