import { useMemo, useState } from "react";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import ResourceForm from "../../components/forms/ResourceForm";
import StatusBadge from "../../components/dashboard/StatusBadge";
import { assetsSeed } from "../../constants/assetManagerData";

const fields = [
  { name: "name", label: "Asset Name", placeholder: "MacBook Pro 14", required: true },
  { name: "category", label: "Category", placeholder: "Laptop", required: true },
  { name: "department", label: "Department", placeholder: "Engineering", required: true },
  { name: "serialNumber", label: "Serial Number", placeholder: "SN-2026-0001", required: true },
  { name: "purchaseDate", label: "Purchase Date", type: "date", required: true },
  { name: "condition", label: "Condition", placeholder: "Excellent", defaultValue: "Good", required: true },
];

function emptyValues() {
  return fields.reduce((values, field) => {
    values[field.name] = field.defaultValue || "";
    return values;
  }, {});
}

export default function RegisterAsset() {
  const [values, setValues] = useState(emptyValues);
  const [registeredAsset, setRegisteredAsset] = useState(null);
  const generatedId = useMemo(
    () => `AST-2026-${String(assetsSeed.length + 1).padStart(3, "0")}`,
    [],
  );

  const handleChange = (event) => {
    const { name, value } = event.target;
    setValues((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setRegisteredAsset({ ...values, id: generatedId, status: "Available" });
    setValues(emptyValues());
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Asset Manager"
        title="Register Asset"
        description="Create a new asset record. The asset ID is generated automatically and status starts as Available."
      />

      <section className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <SectionCard title="Asset Details" description="Fill the asset master data">
          <ResourceForm
            fields={fields}
            values={values}
            onChange={handleChange}
            onSubmit={handleSubmit}
            onCancel={() => setValues(emptyValues())}
            submitLabel="Register Asset"
          />
        </SectionCard>

        <SectionCard title="Generated Record" description="Preview after registration">
          <div className="space-y-4">
            <div className="rounded-2xl bg-[#F8FAFC] p-4">
              <p className="text-sm font-semibold text-slate-500">Next Asset ID</p>
              <p className="mt-2 text-2xl font-semibold text-[#1E293B]">{generatedId}</p>
            </div>
            <StatusBadge tone="success">Status: Available</StatusBadge>
            {registeredAsset && (
              <div className="rounded-2xl border border-[#E2E8F0] p-4">
                <p className="text-sm font-semibold text-[#1E293B]">
                  {registeredAsset.name}
                </p>
                <p className="mt-1 text-sm font-medium text-slate-500">
                  {registeredAsset.id} registered successfully.
                </p>
              </div>
            )}
          </div>
        </SectionCard>
      </section>
    </div>
  );
}
