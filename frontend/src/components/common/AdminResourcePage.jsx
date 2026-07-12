import { Plus } from "lucide-react";
import ConfirmationDialog from "./ConfirmationDialog";
import PageHeader from "../dashboard/PageHeader";
import ResourceForm from "../forms/ResourceForm";
import DataTable from "../tables/DataTable";
import Button from "../ui/Button";
import Modal from "../ui/Modal";
import useResourceCollection from "../../hooks/useResourceCollection";

export default function AdminResourcePage({
  title,
  description,
  eyebrow,
  rows: initialRows,
  columns,
  fields,
  entityName,
  idPrefix,
}) {
  const {
    rows,
    deletingRow,
    formValues,
    isEditing,
    openCreateModal,
    openEditModal,
    closeFormModal,
    setDeletingRow,
    handleChange,
    saveResource,
    deleteResource,
  } = useResourceCollection({ initialRows, fields, idPrefix });
  const modalTitle = isEditing ? `Edit ${entityName}` : `Create ${entityName}`;

  const handleSubmit = (event) => {
    event.preventDefault();
    saveResource();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={eyebrow}
        title={title}
        description={description}
        action={
          <Button onClick={openCreateModal}>
            <Plus size={18} />
            Create {entityName}
          </Button>
        }
      />

      <section className="space-y-4">
        <div>
          <h2 className="text-base font-semibold text-[#1E293B]">
            {entityName}s
          </h2>
          <p className="mt-1 text-sm font-medium text-slate-500">
            Manage records using local dummy data for now.
          </p>
        </div>
        <DataTable
          columns={columns}
          rows={rows}
          onEdit={openEditModal}
          onDelete={setDeletingRow}
          caption={`${entityName} records`}
          emptyTitle={`No ${entityName.toLowerCase()}s yet`}
          emptyDescription={`Create the first ${entityName.toLowerCase()} to start populating this workspace.`}
        />
      </section>

      <Modal
        isOpen={Boolean(formValues)}
        title={modalTitle}
        description="Keep master data clean and consistent across the workspace."
        onClose={closeFormModal}
      >
        {formValues && (
          <ResourceForm
            fields={fields}
            values={formValues}
            onChange={handleChange}
            onSubmit={handleSubmit}
            onCancel={closeFormModal}
            submitLabel={isEditing ? "Save Changes" : `Create ${entityName}`}
          />
        )}
      </Modal>

      <ConfirmationDialog
        isOpen={Boolean(deletingRow)}
        title={`Delete ${entityName}`}
        description={`This will remove ${deletingRow?.name || "this record"} from the local table.`}
        onCancel={() => setDeletingRow(null)}
        onConfirm={deleteResource}
      />
    </div>
  );
}
