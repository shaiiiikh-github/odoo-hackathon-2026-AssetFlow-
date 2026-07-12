import { createContext, useCallback, useEffect, useMemo, useState } from "react";
import { getEmployeeByEmail } from "../mock/employees";
import {
  approveRequest,
  createRequest,
  getAdminRequestSummary,
  getEmployeeAssets,
  getEmployeeRequestSummary,
  getEmployeeProfileForUser,
  getAvailableAssetsForCategory,
  getManagerRequestSummary,
  getNotificationsForUser,
  getRequestById,
  getRequestMetrics,
  getVisibleRequests,
  getUnreadNotificationCount,
  loadAssetRequestState,
  markRequestUnderReview,
  rejectRequest,
  saveAssetRequestState,
} from "../services/assetRequestService";

const AssetRequestContext = createContext(undefined);

export function AssetRequestProvider({ children }) {
  const [state, setState] = useState(() => loadAssetRequestState());

  useEffect(() => {
    saveAssetRequestState(state);
  }, [state]);

  const createNewRequest = useCallback((payload) => {
    setState((current) => createRequest(current, payload));
  }, []);

  const approveAssetRequest = useCallback((payload) => {
    setState((current) => approveRequest(current, payload));
  }, []);

  const rejectAssetRequest = useCallback((payload) => {
    setState((current) => rejectRequest(current, payload));
  }, []);

  const openForReview = useCallback((requestId, manager) => {
    setState((current) => markRequestUnderReview(current, requestId, manager));
  }, []);

  const value = useMemo(
    () => ({
      requests: state.requests,
      assets: state.assets,
      notifications: state.notifications,
      getRequestById: (requestId) => getRequestById(state, requestId),
      getRequestMetrics: (role, userEmail) => getRequestMetrics(state, role, userEmail),
      getVisibleRequests: (role, userEmail) => getVisibleRequests(state, role, userEmail),
      getEmployeeAssets: (userEmail) => getEmployeeAssets(state, userEmail),
      getNotificationsForUser: (role, userEmail) =>
        getNotificationsForUser(state, role, userEmail),
      getUnreadNotificationCount: (role, userEmail) =>
        getUnreadNotificationCount(state, role, userEmail),
      getAvailableAssetsForCategory: (assetCategory) =>
        getAvailableAssetsForCategory(state, assetCategory),
      getEmployeeRequestSummary: (userEmail) =>
        getEmployeeRequestSummary(state, userEmail),
      getManagerRequestSummary: () => getManagerRequestSummary(state),
      getAdminRequestSummary: () => getAdminRequestSummary(state),
      getEmployeeProfileForUser: (user) => getEmployeeProfileForUser(user),
      getEmployeeRecordByEmail: (email) => getEmployeeByEmail(email),
      createRequest: createNewRequest,
      approveRequest: approveAssetRequest,
      rejectRequest: rejectAssetRequest,
      markRequestUnderReview: openForReview,
    }),
    [
      state,
      createNewRequest,
      approveAssetRequest,
      rejectAssetRequest,
      openForReview,
    ],
  );

  return (
    <AssetRequestContext.Provider value={value}>
      {children}
    </AssetRequestContext.Provider>
  );
}

export { AssetRequestContext };