import RequestWorkspace from "../../components/assetRequests/RequestWorkspace";

export default function AssetRequests() {
  return (
    <RequestWorkspace
      mode="admin"
      eyebrow="Admin"
      title="Asset Requests"
      description="Read-only visibility into the enterprise request lifecycle and outcomes."
      createButtonLabel="Request New Asset"
      emptyTitle="No requests on record"
      emptyDescription="Request history will be visible here once employees begin submitting assets."
    />
  );
}