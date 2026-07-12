import { X } from "lucide-react";
import RequestStatusBadge from "./RequestStatusBadge";
import RequestTimeline from "./RequestTimeline";

export default function RequestDetailsDrawer({ request, isOpen, onClose }) {
  if (!isOpen || !request) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[70] flex justify-end">
      <button
        type="button"
        aria-label="Close request drawer"
        className="absolute inset-0 bg-slate-950/40 backdrop-blur-sm"
        onClick={onClose}
      />
      <aside className="relative flex h-full w-full max-w-2xl flex-col overflow-y-auto border-l border-white/80 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.18)] animate-[modal-in_160ms_ease-out]">
        <header className="flex items-start justify-between gap-4 border-b border-[#E2E8F0] p-6">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#2563EB]">Request Details</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-[#0F172A]">{request.id}</h2>
            <p className="mt-2 text-sm font-medium text-slate-500">{request.requestedAsset}</p>
          </div>
          <button
            type="button"
            aria-label="Close"
            className="flex h-9 w-9 items-center justify-center rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#0F172A]"
            onClick={onClose}
          >
            <X size={18} />
          </button>
        </header>

        <div className="space-y-8 p-6">
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <Info label="Employee" value={request.employeeName} />
            <Info label="Department" value={request.department} />
            <Info label="Requested Asset" value={request.requestedAsset} />
            <Info label="Priority" value={request.priority} />
            <Info label="Assigned Manager" value={request.assignedManager || "Not assigned"} />
            <Info label="Status" value={<RequestStatusBadge status={request.status} />} />
          </section>

          <section className="grid gap-4 sm:grid-cols-2">
            <TextCard label="Reason" value={request.reason} />
            <TextCard label="Business Justification" value={request.businessJustification} />
          </section>

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Info label="Requested Date" value={request.requestedDate} />
            <Info label="Required By" value={request.requiredBy} />
            <Info label="Allocated Asset" value={request.allocatedAssetName || "Pending"} />
            <Info label="Approval Notes" value={request.approvalNotes || "No notes yet"} />
          </section>

          <section>
            <h3 className="text-base font-semibold tracking-tight text-[#0F172A]">Timeline</h3>
            <div className="mt-4">
              <RequestTimeline items={request.timeline} />
            </div>
          </section>
        </div>
      </aside>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{label}</p>
      <div className="mt-2 text-sm font-semibold text-[#1E293B]">{value}</div>
    </div>
  );
}

function TextCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4 shadow-sm sm:col-span-1">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{label}</p>
      <p className="mt-2 text-sm font-medium leading-6 text-[#1E293B]">{value}</p>
    </div>
  );
}