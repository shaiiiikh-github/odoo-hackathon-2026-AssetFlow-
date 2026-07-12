import { useState } from "react";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Modal from "../ui/Modal";

export default function RejectModal({ isOpen, onClose, onSubmit, isSubmitting = false }) {
  const [reason, setReason] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    onSubmit(reason);
  }

  return (
    <Modal
      isOpen={isOpen}
      title="Reject Request"
      description="Provide a clear rejection reason for the employee."
      onClose={onClose}
    >
      <form className="space-y-5" onSubmit={handleSubmit}>
        <Input
          label="Reason"
          name="reason"
          type="textarea"
          placeholder="Explain why this request was rejected"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          required
        />

        <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="danger" disabled={isSubmitting || !reason.trim()}>
            {isSubmitting ? "Rejecting..." : "Submit Rejection"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}