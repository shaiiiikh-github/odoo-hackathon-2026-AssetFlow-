import StatusBadge from "../dashboard/StatusBadge";

const tones = {
  Pending: "warning",
  "Under Review": "info",
  Approved: "success",
  Rejected: "danger",
  Allocated: "success",
  Completed: "neutral",
};

export default function RequestStatusBadge({ status }) {
  return <StatusBadge tone={tones[status] || "neutral"}>{status}</StatusBadge>;
}