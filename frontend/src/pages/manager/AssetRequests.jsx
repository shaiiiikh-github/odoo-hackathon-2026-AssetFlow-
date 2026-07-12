import RequestWorkspace from "../../components/assetRequests/RequestWorkspace";

export default function AssetRequests() {
  return (
    <RequestWorkspace
      mode="manager"
      eyebrow="Asset Manager"
      title="Asset Requests"
      description="Review enterprise requests, approve allocations, or reject with notes."
      createButtonLabel="Request New Asset"
      emptyTitle="No requests available"
      emptyDescription="Incoming asset requests will appear here as employees submit them."
    />
  );
}