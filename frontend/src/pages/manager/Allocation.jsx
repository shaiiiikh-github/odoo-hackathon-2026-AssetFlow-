import { useState } from "react";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import ResourceForm from "../../components/forms/ResourceForm";
import DataTable from "../../components/tables/DataTable";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import { allocationSeed } from "../../constants/assetManagerData";

const columns = [
  { key: "id", label: "ID" },
  { key: "asset", label: "Asset" },
  { key: "employee", label: "Employee" },
  { key: "department", label: "Department" },
  { key: "date", label: "Date" },
  { key: "status", label: "Status" },
];

const fields = [
  { name: "asset", label: "Asset", placeholder: "Dell Latitude 7440", required: true },
  { name: "employee", label: "Employee", placeholder: "Rohan Shah", required: true },
  { name: "department", label: "Department", placeholder: "Operations", required: true },
  { name: "date", label: "Allocation Date", type: "date", required: true },
];

const initialValues = { asset: "", employee: "", department: "", date: "" };

export default function Allocation() {
  const [rows, setRows] = useState(allocationSeed);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [values, setValues] = useState(initialValues);

  const handleSubmit = (event) => {
    event.preventDefault();
    setRows((current) => [
      ...current,
      { ...values, id: `ALC-${String(current.length + 1).padStart(3, "0")}`, status: "Allocated" },
    ]);
    setValues(initialValues);
    setIsModalOpen(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Asset Manager"
        title="Allocation"
        description="Assign available assets to employees and track allocation history."
        action={<Button onClick={() => setIsModalOpen(true)}>Allocate Asset</Button>}
      />

      <SectionCard title="Allocation History" description="Recent employee assignments">
        <DataTable
          columns={columns}
          rows={rows}
          onEdit={() => setIsModalOpen(true)}
          caption="Allocation history"
          emptyTitle="No allocations"
          emptyDescription="New asset allocations will appear here."
        />
      </SectionCard>

      <Modal
        isOpen={isModalOpen}
        title="Allocate Asset"
        description="Create a local dummy allocation record."
        onClose={() => setIsModalOpen(false)}
      >
        <ResourceForm
          fields={fields}
          values={values}
          onChange={(event) => setValues((current) => ({ ...current, [event.target.name]: event.target.value }))}
          onSubmit={handleSubmit}
          onCancel={() => setIsModalOpen(false)}
          submitLabel="Allocate Asset"
        />
      </Modal>
    </div>
  );
}
