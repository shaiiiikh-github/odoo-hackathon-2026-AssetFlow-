import { assets as assetSeed } from "../mock/assets";
import { assetRequests as requestSeed, requestCategories, requestPriorities } from "../mock/assetRequests";
import { employees } from "../mock/employees";
import { notifications as notificationSeed } from "../mock/notifications";

const STORAGE_KEY = "assetflow:asset-request-state";

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function canUseStorage() {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function formatToday() {
  return new Date().toISOString().slice(0, 10);
}

function formatTimestamp() {
  return new Date().toISOString();
}

function getEmployeeFromUser(user) {
  if (!user?.email) {
    return null;
  }

  return employees.find(
    (employee) => employee.email.toLowerCase() === user.email.toLowerCase(),
  ) || null;
}

function buildState() {
  return {
    requests: clone(requestSeed),
    assets: clone(assetSeed),
    notifications: clone(notificationSeed),
  };
}

export function loadAssetRequestState() {
  if (!canUseStorage()) {
    return buildState();
  }

  const stored = window.localStorage.getItem(STORAGE_KEY);

  if (!stored) {
    return buildState();
  }

  try {
    const parsed = JSON.parse(stored);
    return {
      requests: Array.isArray(parsed.requests) ? parsed.requests : clone(requestSeed),
      assets: Array.isArray(parsed.assets) ? parsed.assets : clone(assetSeed),
      notifications: Array.isArray(parsed.notifications)
        ? parsed.notifications
        : clone(notificationSeed),
    };
  } catch {
    return buildState();
  }
}

export function saveAssetRequestState(state) {
  if (!canUseStorage()) {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function nextRequestId(requests) {
  return `REQ-${String(2400 + requests.length + 1)}`;
}

function nextNotificationId(notifications) {
  return `NOT-${String(9000 + notifications.length + 1)}`;
}

function createTimelineEntry(status, user, note) {
  return {
    status,
    user,
    note,
    timestamp: formatTimestamp(),
  };
}

function appendNotification(notifications, notification) {
  return [notification, ...notifications];
}

function deriveLatestRequestStatus(requests) {
  return requests[0]?.status || "No requests";
}

export function getEmployeeProfileForUser(user) {
  return getEmployeeFromUser(user);
}

export function getVisibleRequests(state, role, userEmail) {
  const normalizedEmail = userEmail?.toLowerCase();

  if (role === "employee") {
    return state.requests.filter(
      (request) => request.employeeEmail.toLowerCase() === normalizedEmail,
    );
  }

  return state.requests;
}

export function getEmployeeAssets(state, userEmail) {
  const normalizedEmail = userEmail?.toLowerCase();

  return state.assets.filter(
    (asset) => asset.assignedToEmail?.toLowerCase() === normalizedEmail,
  );
}

export function getAvailableAssetsForCategory(state, assetCategory) {
  return state.assets.filter(
    (asset) => asset.status === "Available" && asset.category === assetCategory,
  );
}

export function getRequestById(state, requestId) {
  return state.requests.find((request) => request.id === requestId) || null;
}

export function getNotificationsForUser(state, role, userEmail) {
  const normalizedEmail = userEmail?.toLowerCase();

  return state.notifications
    .filter((notification) => {
      if (role === "employee" || role === "admin") {
        return notification.recipientEmail?.toLowerCase() === normalizedEmail;
      }

      return notification.recipientRole === role;
    })
    .sort((left, right) => new Date(right.createdAt) - new Date(left.createdAt));
}

export function getUnreadNotificationCount(state, role, userEmail) {
  return getNotificationsForUser(state, role, userEmail).filter(
    (notification) => notification.status === "Unread",
  ).length;
}

export function getRequestMetrics(state, role, userEmail) {
  const visibleRequests = getVisibleRequests(state, role, userEmail);
  const pending = visibleRequests.filter((request) => request.status === "Pending").length;
  const approved = visibleRequests.filter((request) => request.status === "Allocated").length;
  const rejected = visibleRequests.filter((request) => request.status === "Rejected").length;
  const allocated = visibleRequests.filter((request) => request.status === "Allocated").length;

  const requestCounts = visibleRequests.reduce((accumulator, request) => {
    accumulator[request.assetCategory] = (accumulator[request.assetCategory] || 0) + 1;
    return accumulator;
  }, {});

  const mostRequestedAsset = Object.entries(requestCounts).sort((left, right) => right[1] - left[1])[0]?.[0] || "Laptop";

  return {
    total: visibleRequests.length,
    pending,
    approved,
    rejected,
    allocated,
    latestStatus: deriveLatestRequestStatus(visibleRequests),
    averageApprovalTime: "4.2h",
    mostRequestedAsset,
  };
}

export function createRequest(state, { employee, values }) {
  const request = {
    id: nextRequestId(state.requests),
    employeeId: employee.id,
    employeeName: employee.name,
    employeeEmail: employee.email,
    department: employee.department,
    assetCategory: values.assetCategory,
    requestedAsset: values.assetCategory,
    priority: values.priority,
    status: "Pending",
    requestedDate: formatToday(),
    requiredBy: values.requiredBy,
    reason: values.reason,
    businessJustification: values.businessJustification,
    assignedManager: null,
    approvalNotes: "",
    allocatedAssetId: null,
    allocatedAssetName: null,
    completedDate: null,
    timeline: [createTimelineEntry("Submitted", employee.name, "Request submitted from employee portal.")],
  };

  const notification = {
    id: nextNotificationId(state.notifications),
    recipientRole: "asset-manager",
    recipientEmail: "manager@assetflow.com",
    title: "New asset request submitted",
    message: `${employee.name} requested ${values.assetCategory} with ${values.priority.toLowerCase()} priority.`,
    createdAt: formatTimestamp(),
    status: "Unread",
  };

  return {
    ...state,
    requests: [request, ...state.requests],
    notifications: appendNotification(state.notifications, notification),
  };
}

function updateAssetAllocation(assets, request, selectedAssetId, managerName) {
  return assets.map((asset) => {
    if (asset.id !== selectedAssetId) {
      return asset;
    }

    return {
      ...asset,
      status: "Allocated",
      assignedToEmail: request.employeeEmail,
      assignedToName: request.employeeName,
      assignedDate: formatToday(),
      department: request.department,
      allocatedBy: managerName,
    };
  });
}

export function approveRequest(state, { requestId, selectedAssetId, manager }) {
  const request = getRequestById(state, requestId);

  if (!request) {
    return state;
  }

  const selectedAsset = state.assets.find((asset) => asset.id === selectedAssetId);
  const managerName = manager?.name || "Asset Manager";
  const allocatedAssetName = selectedAsset?.name || request.requestedAsset;
  const updatedRequests = state.requests.map((current) => {
    if (current.id !== requestId) {
      return current;
    }

    const nextTimeline = [
      ...current.timeline,
      createTimelineEntry("Under Review", managerName, "Manager started the allocation review."),
      createTimelineEntry("Approved", managerName, "Request approved for allocation."),
      createTimelineEntry("Allocated", managerName, `Allocated ${allocatedAssetName} to ${current.employeeName}.`),
    ];

    return {
      ...current,
      status: "Allocated",
      assignedManager: managerName,
      approvalNotes: selectedAsset
        ? `Allocated ${selectedAsset.name} from available stock.`
        : "Approved for allocation.",
      allocatedAssetId: selectedAssetId,
      allocatedAssetName,
      completedDate: null,
      timeline: nextTimeline,
    };
  });

  const updatedAssets = updateAssetAllocation(state.assets, request, selectedAssetId, managerName);

  const notification = {
    id: nextNotificationId(state.notifications),
    recipientRole: "employee",
    recipientEmail: request.employeeEmail,
    title: "Asset request approved",
    message: `${allocatedAssetName} has been allocated to your request ${request.id}.`,
    createdAt: formatTimestamp(),
    status: "Unread",
  };

  return {
    ...state,
    requests: updatedRequests,
    assets: updatedAssets,
    notifications: appendNotification(state.notifications, notification),
  };
}

export function rejectRequest(state, { requestId, reason, manager }) {
  const request = getRequestById(state, requestId);

  if (!request) {
    return state;
  }

  const managerName = manager?.name || "Asset Manager";

  const updatedRequests = state.requests.map((current) => {
    if (current.id !== requestId) {
      return current;
    }

    return {
      ...current,
      status: "Rejected",
      assignedManager: managerName,
      approvalNotes: reason,
      timeline: [
        ...current.timeline,
        createTimelineEntry("Under Review", managerName, "Manager started the review process."),
        createTimelineEntry("Rejected", managerName, reason),
      ],
    };
  });

  const notification = {
    id: nextNotificationId(state.notifications),
    recipientRole: "employee",
    recipientEmail: request.employeeEmail,
    title: "Asset request rejected",
    message: `Request ${request.id} was rejected: ${reason}`,
    createdAt: formatTimestamp(),
    status: "Unread",
  };

  return {
    ...state,
    requests: updatedRequests,
    notifications: appendNotification(state.notifications, notification),
  };
}

export function markRequestUnderReview(state, requestId, manager) {
  const request = getRequestById(state, requestId);

  if (!request || request.status !== "Pending") {
    return state;
  }

  const managerName = manager?.name || "Asset Manager";

  return {
    ...state,
    requests: state.requests.map((current) => {
      if (current.id !== requestId) {
        return current;
      }

      return {
        ...current,
        status: "Under Review",
        assignedManager: managerName,
        timeline: [
          ...current.timeline,
          createTimelineEntry("Under Review", managerName, "Manager opened the request for review."),
        ],
      };
    }),
  };
}

export function getEmployeeRequestSummary(state, userEmail) {
  const requests = getVisibleRequests(state, "employee", userEmail);

  return {
    pending: requests.filter((request) => request.status === "Pending" || request.status === "Under Review").length,
    approved: requests.filter((request) => request.status === "Allocated").length,
    rejected: requests.filter((request) => request.status === "Rejected").length,
    latestStatus: deriveLatestRequestStatus(requests),
  };
}

export function getManagerRequestSummary(state) {
  const requests = getVisibleRequests(state, "asset-manager");

  return {
    pending: requests.filter((request) => request.status === "Pending").length,
    approvedToday: requests.filter((request) => request.status === "Allocated").length,
    rejectedToday: requests.filter((request) => request.status === "Rejected").length,
    averageApprovalTime: "4.2h",
    mostRequestedAsset:
      requests.reduce((winner, request) => {
        if (!winner) {
          return request.assetCategory;
        }

        const winnerCount = requests.filter((item) => item.assetCategory === winner).length;
        const currentCount = requests.filter((item) => item.assetCategory === request.assetCategory).length;

        return currentCount > winnerCount ? request.assetCategory : winner;
      }, null) || "Laptop",
  };
}

export function getAdminRequestSummary(state) {
  const requests = state.requests;

  return {
    total: requests.length,
    pending: requests.filter((request) => request.status === "Pending").length,
    approved: requests.filter((request) => request.status === "Allocated").length,
    rejected: requests.filter((request) => request.status === "Rejected").length,
  };
}

export { requestCategories, requestPriorities };