import { useMemo, useState } from "react";
import { AlertCircle, ClipboardList, Clock3, RotateCcw, ShieldCheck } from "lucide-react";
import useAuth from "../../hooks/useAuth";
import useAssetRequests from "../../hooks/useAssetRequests";
import Button from "../ui/Button";
import PageHeader from "../dashboard/PageHeader";
import SectionCard from "../dashboard/SectionCard";
import StatsGrid from "../dashboard/StatsGrid";
import RequestCard from "./RequestCard";
import RequestFilters from "./RequestFilters";
import RequestTable from "./RequestTable";
import RequestDetailsDrawer from "./RequestDetailsDrawer";
import RequestFormModal from "./RequestFormModal";
import ApprovalModal from "./ApprovalModal";
import RejectModal from "./RejectModal";

export default function RequestWorkspace({
  mode,
  eyebrow,
  title,
  description,
  createButtonLabel,
  emptyTitle,
  emptyDescription,
}) {
  const { user, role } = useAuth();
  const requestApi = useAssetRequests();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [priorityFilter, setPriorityFilter] = useState("All");
  const [selectedRequestId, setSelectedRequestId] = useState(null);
  const [isRequestModalOpen, setIsRequestModalOpen] = useState(false);
  const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
  const [isRejectModalOpen, setIsRejectModalOpen] = useState(false);
  const [requestFormNonce, setRequestFormNonce] = useState(0);
  const [approvalNonce, setApprovalNonce] = useState(0);
  const [rejectNonce, setRejectNonce] = useState(0);
  const [isBusy, setIsBusy] = useState(false);

  const currentEmployee =
    requestApi.getEmployeeProfileForUser(user) ||
    requestApi.getEmployeeRecordByEmail(user.email) || {
      id: user.email,
      name: user.name,
      email: user.email,
      department: "Unknown",
      role,
      initials: user.initials,
    };
  const visibleRequests = requestApi.getVisibleRequests(role, user.email);
  const filteredRequests = useMemo(
    () =>
      visibleRequests.filter((request) => {
        const text = `${request.id} ${request.employeeName} ${request.department} ${request.requestedAsset} ${request.assetCategory}`.toLowerCase();
        const matchesSearch = text.includes(search.toLowerCase());
        const matchesStatus = statusFilter === "All" || request.status === statusFilter;
        const matchesPriority = priorityFilter === "All" || request.priority === priorityFilter;

        return matchesSearch && matchesStatus && matchesPriority;
      }),
    [priorityFilter, search, statusFilter, visibleRequests],
  );

  const selectedRequest = selectedRequestId ? requestApi.getRequestById(selectedRequestId) : null;
  const availableAssets = selectedRequest
    ? requestApi.getAvailableAssetsForCategory(selectedRequest.assetCategory)
    : [];
  const metrics = requestApi.getRequestMetrics(role, user.email);
  const stats = buildStats(mode, metrics);
  const columns = buildColumns();

  function openDetails(request) {
    setSelectedRequestId(request.id);
    if (mode === "manager") {
      requestApi.markRequestUnderReview(request.id, user);
    }
  }

  function closeDetails() {
    setSelectedRequestId(null);
  }

  function openRequestForm() {
    setRequestFormNonce((value) => value + 1);
    setIsRequestModalOpen(true);
  }

  function openApproval(request) {
    setSelectedRequestId(request.id);
    requestApi.markRequestUnderReview(request.id, user);
    setApprovalNonce((value) => value + 1);
    setIsApprovalModalOpen(true);
  }

  function openReject(request) {
    setSelectedRequestId(request.id);
    requestApi.markRequestUnderReview(request.id, user);
    setRejectNonce((value) => value + 1);
    setIsRejectModalOpen(true);
  }

  function submitRequest(values) {
    setIsBusy(true);
    requestApi.createRequest({ employee: currentEmployee, values });
    setIsBusy(false);
  }

  function confirmAllocation(values) {
    if (!selectedRequestId) {
      return;
    }

    setIsBusy(true);
    requestApi.approveRequest({
      requestId: selectedRequestId,
      selectedAssetId: values.selectedAssetId,
      manager: user,
    });
    setIsBusy(false);
    setIsApprovalModalOpen(false);
    closeDetails();
  }

  function confirmRejection(reason) {
    if (!selectedRequestId) {
      return;
    }

    setIsBusy(true);
    requestApi.rejectRequest({
      requestId: selectedRequestId,
      reason,
      manager: user,
    });
    setIsBusy(false);
    setIsRejectModalOpen(false);
    closeDetails();
  }

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow={eyebrow}
        title={title}
        description={description}
        action={mode === "employee" ? <Button onClick={openRequestForm}>{createButtonLabel}</Button> : undefined}
      />

      {mode !== "employee" && <StatsGrid items={stats} />}

      <SectionCard
        title={mode === "employee" ? "My Requests" : "Request Register"}
        description={
          mode === "employee"
            ? "A compact view of your requests with detailed information in the drawer."
            : "Search, filter, and review requests without losing the full record in the drawer."
        }
        action={mode !== "employee" ? <span className="text-sm font-semibold text-slate-400">Read only for admins</span> : undefined}
      >
        <div className="space-y-6">
          <RequestFilters
            search={search}
            status={statusFilter}
            priority={priorityFilter}
            onSearchChange={setSearch}
            onStatusChange={setStatusFilter}
            onPriorityChange={setPriorityFilter}
            showPriority
          />

          {mode === "employee" ? (
            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
              {filteredRequests.map((request) => (
                <RequestCard
                  key={request.id}
                  request={request}
                  variant="summary"
                  onClick={() => openDetails(request)}
                />
              ))}
              {!filteredRequests.length && (
                <div className="md:col-span-2 xl:col-span-3">
                  <p className="rounded-[1.25rem] border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-sm font-medium text-slate-500">
                    No requests match the current filters.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <RequestTable
              columns={columns}
              rows={filteredRequests}
              caption="Asset requests register"
              emptyTitle={emptyTitle}
              emptyDescription={emptyDescription}
              onView={openDetails}
              onApprove={mode === "manager" ? openApproval : undefined}
              onReject={mode === "manager" ? openReject : undefined}
              readOnly={mode === "admin"}
            />
          )}
        </div>
      </SectionCard>

      <RequestDetailsDrawer request={selectedRequest} isOpen={Boolean(selectedRequest)} onClose={closeDetails} />

      <RequestFormModal
        key={`request-form-${requestFormNonce}`}
        isOpen={isRequestModalOpen}
        onClose={() => setIsRequestModalOpen(false)}
        onSubmit={submitRequest}
        requestCount={requestApi.requests.length}
        isSubmitting={isBusy}
      />

      <ApprovalModal
        key={`approval-modal-${approvalNonce}`}
        request={selectedRequest}
        assets={availableAssets}
        isOpen={isApprovalModalOpen}
        onClose={() => setIsApprovalModalOpen(false)}
        onSubmit={confirmAllocation}
        isSubmitting={isBusy}
      />

      <RejectModal
        key={`reject-modal-${rejectNonce}`}
        isOpen={isRejectModalOpen}
        onClose={() => setIsRejectModalOpen(false)}
        onSubmit={confirmRejection}
        isSubmitting={isBusy}
      />
    </div>
  );
}

function buildColumns() {
  return [
    { key: "id", label: "Request ID" },
    { key: "employeeName", label: "Employee" },
    { key: "assetCategory", label: "Asset Type", render: (row) => row.assetCategory },
    { key: "priority", label: "Priority" },
    { key: "status", label: "Status" },
  ];
}

function buildStats(mode, metrics) {
  if (mode === "employee") {
    return [
      { label: "Pending Requests", value: String(metrics.pending), change: "Awaiting review", tone: "amber", icon: Clock3 },
      { label: "Approved Requests", value: String(metrics.approved), change: "Allocated assets", tone: "emerald", icon: ShieldCheck },
      { label: "Rejected Requests", value: String(metrics.rejected), change: "Needs follow up", tone: "rose", icon: AlertCircle },
      { label: "Latest Status", value: metrics.latestStatus, change: "Most recent request", tone: "blue", icon: RotateCcw },
    ];
  }

  if (mode === "manager") {
    return [
      { label: "Pending", value: String(metrics.pending), change: "Awaiting review", tone: "amber", icon: Clock3 },
      { label: "Approved", value: String(metrics.approved), change: "Allocated requests", tone: "emerald", icon: ShieldCheck },
      { label: "Rejected", value: String(metrics.rejected), change: "Declined requests", tone: "rose", icon: AlertCircle },
      { label: "Allocated", value: String(metrics.allocated), change: "Ready with assignee", tone: "blue", icon: ClipboardList },
    ];
  }

  return [
    { label: "Total Requests", value: String(metrics.total), change: "Request register", tone: "blue", icon: ClipboardList },
    { label: "Pending", value: String(metrics.pending), change: "Awaiting review", tone: "amber", icon: Clock3 },
    { label: "Approved", value: String(metrics.approved), change: "Allocated requests", tone: "emerald", icon: ShieldCheck },
    { label: "Rejected", value: String(metrics.rejected), change: "Declined requests", tone: "rose", icon: AlertCircle },
  ];
}