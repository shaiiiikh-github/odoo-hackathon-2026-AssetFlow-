import { ChevronRight, FileText } from "lucide-react";
import { Link } from "react-router-dom";
import RequestStatusBadge from "./RequestStatusBadge";

export default function RequestCard({ request, to, onClick, variant = "detail" }) {
  const Wrapper = to ? Link : "button";
  const wrapperProps = to ? { to } : { type: "button", onClick };

  return (
    <Wrapper
      {...wrapperProps}
      className={`group flex w-full items-start gap-4 rounded-[1.25rem] border border-[#E2E8F0] bg-white p-5 text-left shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-[#2563EB] hover:shadow-[0_12px_24px_rgba(37,99,235,0.08)] ${
        variant === "summary" ? "flex-col" : ""
      }`}
    >
      <div className={`flex w-full items-start gap-4 ${variant === "summary" ? "justify-between" : ""}`}>
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-[#2563EB] ring-1 ring-blue-100">
          <FileText size={18} />
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex items-start justify-between gap-3">
            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold text-[#0F172A]">
                {variant === "summary" ? request.assetCategory : request.requestedAsset}
              </span>
              <span className="mt-1 block text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
                {request.id}
              </span>
            </span>
            <RequestStatusBadge status={request.status} />
          </span>
          {variant !== "summary" && (
            <span className="mt-3 block text-sm font-medium leading-6 text-slate-500">
              {request.reason}
            </span>
          )}
        </span>
        {to && variant !== "summary" && (
          <ChevronRight
            size={18}
            className="mt-1 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-[#2563EB]"
          />
        )}
      </div>

      {variant === "summary" && (
        <div className="grid w-full gap-3 border-t border-[#E2E8F0] pt-4 sm:grid-cols-2">
          <Detail label="Asset Type" value={request.assetCategory} />
          <Detail label="Status" value={<RequestStatusBadge status={request.status} />} />
          <Detail label="Priority" value={request.priority} />
          <Detail label="Requested Date" value={request.requestedDate} />
        </div>
      )}

      {variant === "summary" && (
        <div className="flex w-full items-center justify-between border-t border-[#E2E8F0] pt-4">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
            View the full request in the drawer
          </p>
          <span className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-[#2563EB] ring-1 ring-blue-100">
            View Details
          </span>
        </div>
      )}

      {to && variant !== "summary" && (
        <ChevronRight
          size={18}
          className="mt-1 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-[#2563EB]"
        />
      )}
    </Wrapper>
  );
}

function Detail({ label, value }) {
  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">{label}</p>
      <div className="mt-1 text-sm font-semibold text-[#0F172A]">{value}</div>
    </div>
  );
}