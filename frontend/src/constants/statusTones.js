export const STATUS_TONES = {
  active: "success",
  approved: "success",
  allocated: "info",
  available: "success",
  completed: "success",
  inactive: "neutral",
  maintenance: "warning",
  pending: "warning",
  read: "neutral",
  unread: "info",
};

export function getStatusTone(status, fallback = "neutral") {
  return STATUS_TONES[String(status).toLowerCase()] || fallback;
}
