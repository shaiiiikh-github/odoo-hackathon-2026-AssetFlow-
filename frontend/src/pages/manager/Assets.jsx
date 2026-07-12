import { useState } from "react";
import AssetCard from "../../components/manager/AssetCard";
import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import StatsGrid from "../../components/dashboard/StatsGrid";
import DataTable from "../../components/tables/DataTable";
import Modal from "../../components/ui/Modal";
import Button from "../../components/ui/Button";
import { assetSummary, assetsSeed } from "../../constants/assetManagerData";

const columns = [
  { key: "id", label: "Asset ID" },
  { key: "name", label: "Asset" },
  { key: "category", label: "Category" },
  { key: "department", label: "Department" },
  { key: "assignee", label: "Assignee" },
  { key: "status", label: "Status" },
];

export default function Assets() {
  const [selectedAsset, setSelectedAsset] = useState(null);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Asset Manager"
        title="Assets"
        description="Monitor inventory, ownership, and lifecycle status across the organization."
      />

      <StatsGrid items={assetSummary} />

      <section className="grid gap-6 lg:grid-cols-2 xl:grid-cols-4">
        {assetsSeed.map((asset) => (
          <AssetCard key={asset.id} asset={asset} />
        ))}
      </section>

      <SectionCard title="Asset Table" description="Complete asset inventory">
        <DataTable
          columns={columns}
          rows={assetsSeed}
          onEdit={setSelectedAsset}
          caption="Asset inventory"
          emptyTitle="No assets"
          emptyDescription="Registered assets will appear here."
        />
      </SectionCard>

      <Modal
        isOpen={Boolean(selectedAsset)}
        title={selectedAsset?.name}
        description="Asset details are read-only in this dummy workflow."
        onClose={() => setSelectedAsset(null)}
      >
        <div className="space-y-4">
          <AssetCard asset={selectedAsset || assetsSeed[0]} />
          <div className="flex justify-end">
            <Button variant="secondary" onClick={() => setSelectedAsset(null)}>
              Close
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
