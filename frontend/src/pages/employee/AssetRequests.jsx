import RequestWorkspace from "../../components/assetRequests/RequestWorkspace";

export default function AssetRequests() {
  return (
    <RequestWorkspace
      mode="employee"
      eyebrow="Employee"
      title="Asset Requests"
      description="Submit and track your company asset requests from a single workspace."
      createButtonLabel="+ Request New Asset"
      emptyTitle="No requests yet"
      emptyDescription="Your submitted asset requests will appear here with live status updates."
    />
  );
}