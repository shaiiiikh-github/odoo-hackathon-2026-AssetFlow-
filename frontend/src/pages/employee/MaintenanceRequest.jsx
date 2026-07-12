import { useState } from "react";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import StatusBadge from "../../components/dashboard/StatusBadge";
import ResourceForm from "../../components/forms/ResourceForm";
import { employeeAssets } from "../../constants/employeeData";

const fields = [
  { name: "asset", label: "Asset", placeholder: "MacBook Pro 14", required: true },
  { name: "priority", label: "Priority", placeholder: "Low, Medium, or High", required: true },
  { name: "issue", label: "Issue Summary", placeholder: "Battery drains quickly", required: true },
  { name: "description", label: "Description", type: "textarea", placeholder: "Describe the problem and impact.", required: true },
];

const initialValues = { asset: "", priority: "", issue: "", description: "" };

export default function MaintenanceRequest() {
  const [values, setValues] = useState(initialValues);
  const [submittedRequest, setSubmittedRequest] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    setSubmittedRequest({ ...values, id: "REQ-NEW-001", status: "Pending" });
    setValues(initialValues);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Employee"
        title="Maintenance Request"
        description="Raise a maintenance request for one of your assigned assets."
      />

      <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <SectionCard title="Request Details" description="Submit issue information">
          <ResourceForm
            fields={fields}
            values={values}
            onChange={(event) => setValues((current) => ({ ...current, [event.target.name]: event.target.value }))}
            onSubmit={handleSubmit}
            onCancel={() => setValues(initialValues)}
            submitLabel="Submit Request"
          />
        </SectionCard>

        <SectionCard title="Eligible Assets" description="Assets available for requests">
          <div className="space-y-3">
            {employeeAssets.slice(0, 3).map((asset) => (
              <div key={asset.id} className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4">
                <p className="text-sm font-semibold text-[#1E293B]">{asset.name}</p>
                <p className="mt-1 text-xs font-semibold text-slate-500">{asset.id}</p>
              </div>
            ))}
            {submittedRequest && (
              <div className="rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
                <StatusBadge tone="success">{submittedRequest.status}</StatusBadge>
                <p className="mt-3 text-sm font-semibold text-[#1E293B]">
                  {submittedRequest.issue}
                </p>
              </div>
            )}
          </div>
        </SectionCard>
      </section>
    </div>
  );
}
