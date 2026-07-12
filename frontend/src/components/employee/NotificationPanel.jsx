import StatusBadge from "../dashboard/StatusBadge";
import SectionCard from "../dashboard/SectionCard";

export default function NotificationPanel({ notifications }) {
  return (
    <SectionCard title="Notifications" description="Latest employee updates">
      <div className="space-y-3">
        {notifications.map(({ id, title, message, time, status, icon: Icon }) => (
          <article
            key={id}
            className="flex gap-3 rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4"
          >
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white text-[#2563EB]">
              <Icon size={18} />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-sm font-semibold text-[#1E293B]">{title}</h3>
                <StatusBadge tone={status === "Unread" ? "info" : "neutral"}>
                  {status}
                </StatusBadge>
              </div>
              <p className="mt-1 text-sm font-medium leading-6 text-slate-500">
                {message}
              </p>
              <p className="mt-2 text-xs font-semibold text-slate-400">{time}</p>
            </div>
          </article>
        ))}
      </div>
    </SectionCard>
  );
}
