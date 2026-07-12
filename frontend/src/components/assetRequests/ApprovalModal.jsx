import { useState } from "react";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Modal from "../ui/Modal";

export default function ApprovalModal({
  request,
  assets,
  isOpen,
  onClose,
  onSubmit,
  isSubmitting = false,
}) {
  const [selectedAssetId, setSelectedAssetId] = useState(() => assets[0]?.id || "");
  const [notes, setNotes] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit({ selectedAssetId, notes });
  }

  return (
    <Modal
      isOpen={isOpen}
      title="Approve and Allocate"
      description={`Select an available ${request?.assetCategory || "asset"} to assign to this request.`}
      onClose={onClose}
    >
      <form className="space-y-5" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-semibold text-[#1E293B]">Available Asset</span>
          <select
            value={selectedAssetId}
            onChange={(event) => setSelectedAssetId(event.target.value)}
            className="mt-2 h-11 w-full rounded-2xl border border-[#E2E8F0] bg-white px-4 text-sm font-medium text-[#1E293B] outline-none transition duration-200 focus:border-[#2563EB] focus:ring-4 focus:ring-blue-100"
          >
            {assets.length ? (
              assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name} • {asset.id}
                </option>
              ))
            ) : (
              <option value="">No available assets</option>
            )}
          </select>
        </label>

        <Input
          label="Approval Notes"
          name="approvalNotes"
          type="textarea"
          placeholder="Optional allocation notes for the employee"
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
        />

        <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting || !selectedAssetId}>
            {isSubmitting ? "Allocating..." : "Confirm Allocation"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}