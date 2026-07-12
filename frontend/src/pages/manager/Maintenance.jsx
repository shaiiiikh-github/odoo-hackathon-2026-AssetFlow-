import { useState } from "react";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import StatsGrid from "../../components/dashboard/StatsGrid";
import DataTable from "../../components/tables/DataTable";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import StatusBadge from "../../components/dashboard/StatusBadge";
import { maintenanceSeed, requestStats } from "../../constants/assetManagerData";

const columns = [
  { key: "id", label: "Request ID" },
  { key: "asset", label: "Asset" },
  { key: "requester", label: "Requester" },
  { key: "issue", label: "Issue" },
  { key: "priority", label: "Priority" },
  { key: "status", label: "Status" },
];

export default function Maintenance() {
  const [requests, setRequests] = useState(maintenanceSeed);
  const [selectedRequest, setSelectedRequest] = useState(null);

  const updateStatus = (status) => {
    setRequests((current) =>
      current.map((request) =>
        request.id === selectedRequest.id ? { ...request, status } : request,
      ),
    );
    setSelectedRequest(null);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Asset Manager"
        title="Maintenance"
        description="Review, approve, and complete maintenance requests from employees."
      />

      <StatsGrid items={requestStats} />

      <SectionCard title="Maintenance Requests" description="Dummy request queue">
        <DataTable
          columns={columns}
          rows={requests}
          onEdit={setSelectedRequest}
          caption="Maintenance requests"
          emptyTitle="No maintenance requests"
          emptyDescription="Employee maintenance requests will appear here."
        />
      </SectionCard>

      <Modal
        isOpen={Boolean(selectedRequest)}
        title={selectedRequest?.asset}
        description="Review the maintenance request and update its status."
        onClose={() => setSelectedRequest(null)}
      >
        {selectedRequest && (
          <div className="space-y-5">
            <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-sm font-semibold text-[#1E293B]">
                  {selectedRequest.issue}
                </p>
                <StatusBadge tone="warning">{selectedRequest.priority}</StatusBadge>
              </div>
              <p className="mt-2 text-sm font-medium text-slate-500">
                Requested by {selectedRequest.requester}
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:justify-end">
              <Button variant="secondary" onClick={() => setSelectedRequest(null)}>
                Close
              </Button>
              <Button variant="secondary" onClick={() => updateStatus("Approved")}>
                Approve
              </Button>
              <Button onClick={() => updateStatus("Completed")}>
                Mark Complete
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
