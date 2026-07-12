import EmployeeAssetCard from "../../components/employee/EmployeeAssetCard";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import DataTable from "../../components/tables/DataTable";
import { employeeAssets } from "../../constants/employeeData";

const columns = [
  { key: "id", label: "Asset ID" },
  { key: "name", label: "Asset" },
  { key: "category", label: "Category" },
  { key: "assignedDate", label: "Assigned" },
  { key: "condition", label: "Condition" },
  { key: "status", label: "Status" },
];

export default function MyAssets() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Employee"
        title="My Assets"
        description="View every company asset currently assigned to you."
      />

      <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {employeeAssets.map((asset) => (
          <EmployeeAssetCard key={asset.id} asset={asset} />
        ))}
      </section>

      <SectionCard title="Asset Register" description="Assigned asset list">
        <DataTable
          columns={columns}
          rows={employeeAssets}
          caption="Assigned employee assets"
          emptyTitle="No assigned assets"
          emptyDescription="Assigned assets will appear here once allocation is complete."
        />
      </SectionCard>
    </div>
  );
}
