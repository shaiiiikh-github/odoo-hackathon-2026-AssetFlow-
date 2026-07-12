import { useState } from "react";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import StatusBadge from "../../components/dashboard/StatusBadge";
import ResourceForm from "../../components/forms/ResourceForm";
import { employeeAssets } from "../../constants/employeeData";

const fields = [
  { name: "asset", label: "Asset", placeholder: "Magic Keyboard", required: true },
  { name: "returnDate", label: "Preferred Return Date", type: "date", required: true },
  { name: "reason", label: "Reason", placeholder: "No longer needed", required: true },
  { name: "notes", label: "Notes", type: "textarea", placeholder: "Add condition notes or pickup details.", required: true },
];

const initialValues = { asset: "", returnDate: "", reason: "", notes: "" };

export default function ReturnRequest() {
  const [values, setValues] = useState(initialValues);
  const [submittedReturn, setSubmittedReturn] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    setSubmittedReturn({ ...values, id: "RET-NEW-001", status: "Pending" });
    setValues(initialValues);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Employee"
        title="Return Request"
        description="Request to return assigned assets that are no longer needed."
      />

      <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <SectionCard title="Return Details" description="Submit return information">
          <ResourceForm
            fields={fields}
            values={values}
            onChange={(event) => setValues((current) => ({ ...current, [event.target.name]: event.target.value }))}
            onSubmit={handleSubmit}
            onCancel={() => setValues(initialValues)}
            submitLabel="Submit Return"
          />
        </SectionCard>

        <SectionCard title="Return Preview" description="Dummy request confirmation">
          <div className="space-y-3">
            {employeeAssets.slice(0, 2).map((asset) => (
              <div key={asset.id} className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4">
                <p className="text-sm font-semibold text-[#1E293B]">{asset.name}</p>
                <p className="mt-1 text-xs font-semibold text-slate-500">{asset.condition}</p>
              </div>
            ))}
            {submittedReturn && (
              <div className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
                <StatusBadge tone="info">{submittedReturn.status}</StatusBadge>
                <p className="mt-3 text-sm font-semibold text-[#1E293B]">
                  {submittedReturn.asset}
                </p>
              </div>
            )}
          </div>
        </SectionCard>
      </section>
    </div>
  );
}
