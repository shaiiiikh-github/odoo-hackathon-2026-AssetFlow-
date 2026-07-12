const now = "2026-07-12T09:30:00.000Z";

function timelineItem(status, user, timestamp, note) {
  return { status, user, timestamp, note };
}

export const requestCategories = [
  "Laptop",
  "Desktop",
  "Monitor",
  "Keyboard",
  "Mouse",
  "Docking Station",
  "Printer",
  "Projector",
  "Headset",
  "Software License",
];

export const requestPriorities = ["Low", "Medium", "High"];

export const requestStatuses = [
  "Pending",
  "Under Review",
  "Approved",
  "Rejected",
  "Allocated",
  "Completed",
];

export const assetRequests = [
  {
    id: "REQ-2401",
    employeeId: "EMP-1001",
    employeeName: "Emily Carter",
    employeeEmail: "employee@assetflow.com",
    department: "Finance",
    assetCategory: "Laptop",
    requestedAsset: "MacBook Pro 14",
    priority: "High",
    status: "Allocated",
    requestedDate: "2026-07-08",
    requiredBy: "2026-07-15",
    reason: "Need a secure laptop for month-end reporting and vendor reviews.",
    businessJustification:
      "Finance operations require encrypted hardware for approvals, audits, and remote work.",
    assignedManager: "Marcus Reed",
    approvalNotes: "Allocated from stock after approving secure baseline image.",
    allocatedAssetId: "AST-LAP-001",
    allocatedAssetName: "MacBook Pro 14",
    completedDate: null,
    timeline: [
      timelineItem(
        "Submitted",
        "Emily Carter",
        "2026-07-08T08:15:00.000Z",
        "Asset request submitted for finance operations.",
      ),
      timelineItem(
        "Under Review",
        "Marcus Reed",
        "2026-07-08T10:20:00.000Z",
        "Manager started the review process.",
      ),
      timelineItem(
        "Approved",
        "Marcus Reed",
        "2026-07-08T11:05:00.000Z",
        "Request approved and moved to allocation.",
      ),
      timelineItem(
        "Allocated",
        "Marcus Reed",
        "2026-07-08T11:20:00.000Z",
        "MacBook Pro 14 allocated to the requester.",
      ),
    ],
  },
  {
    id: "REQ-2402",
    employeeId: "EMP-1004",
    employeeName: "Neha Kapoor",
    employeeEmail: "neha.kapoor@assetflow.com",
    department: "Engineering",
    assetCategory: "Monitor",
    requestedAsset: "Dell Monitor 27",
    priority: "Medium",
    status: "Under Review",
    requestedDate: "2026-07-10",
    requiredBy: "2026-07-16",
    reason: "Dual monitor setup is required for code reviews and design validation.",
    businessJustification:
      "Improves engineering throughput and reduces context switching during review cycles.",
    assignedManager: "Marcus Reed",
    approvalNotes: "",
    allocatedAssetId: null,
    allocatedAssetName: null,
    completedDate: null,
    timeline: [
      timelineItem(
        "Submitted",
        "Neha Kapoor",
        "2026-07-10T09:40:00.000Z",
        "New request created for engineering productivity.",
      ),
      timelineItem(
        "Under Review",
        "Marcus Reed",
        "2026-07-10T10:05:00.000Z",
        "Manager reviewing available stock.",
      ),
    ],
  },
  {
    id: "REQ-2403",
    employeeId: "EMP-1005",
    employeeName: "Arjun Mehta",
    employeeEmail: "arjun.mehta@assetflow.com",
    department: "Sales",
    assetCategory: "Headset",
    requestedAsset: "Jabra Evolve2 65",
    priority: "Low",
    status: "Rejected",
    requestedDate: "2026-07-04",
    requiredBy: "2026-07-11",
    reason: "Need a headset for customer calls and demo sessions.",
    businessJustification:
      "A dedicated headset improves call quality and reduces ambient noise during demos.",
    assignedManager: "Marcus Reed",
    approvalNotes: "Recommend submitting after headset inventory is replenished.",
    allocatedAssetId: null,
    allocatedAssetName: null,
    completedDate: null,
    timeline: [
      timelineItem(
        "Submitted",
        "Arjun Mehta",
        "2026-07-04T14:25:00.000Z",
        "Sales asset request submitted.",
      ),
      timelineItem(
        "Under Review",
        "Marcus Reed",
        "2026-07-04T15:05:00.000Z",
        "Manager began evaluating the request.",
      ),
      timelineItem(
        "Rejected",
        "Marcus Reed",
        "2026-07-04T15:45:00.000Z",
        "No spare stock available in the requested category.",
      ),
    ],
  },
  {
    id: "REQ-2404",
    employeeId: "EMP-1001",
    employeeName: "Emily Carter",
    employeeEmail: "employee@assetflow.com",
    department: "Finance",
    assetCategory: "Software License",
    requestedAsset: "Microsoft 365 E3",
    priority: "Medium",
    status: "Pending",
    requestedDate: "2026-07-12",
    requiredBy: "2026-07-18",
    reason: "Need enterprise document editing and secure collaboration features.",
    businessJustification:
      "Required for finance reporting, secure document sharing, and audit-ready workflows.",
    assignedManager: null,
    approvalNotes: "",
    allocatedAssetId: null,
    allocatedAssetName: null,
    completedDate: null,
    timeline: [
      timelineItem(
        "Submitted",
        "Emily Carter",
        now,
        "Submitted from the employee portal.",
      ),
    ],
  },
];