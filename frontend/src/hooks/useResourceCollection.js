import { useMemo, useState } from "react";

export function createEmptyValues(fields) {
  return fields.reduce((values, field) => {
    values[field.name] = field.defaultValue || "";
    return values;
  }, {});
}

export default function useResourceCollection({ initialRows, fields, idPrefix }) {
  const [rows, setRows] = useState(initialRows);
  const [editingRow, setEditingRow] = useState(null);
  const [deletingRow, setDeletingRow] = useState(null);
  const [formValues, setFormValues] = useState(null);

  const nextId = useMemo(() => {
    const numericIds = rows
      .map((row) => Number(String(row.id).split("-").at(-1)))
      .filter(Number.isFinite);
    const nextNumber = Math.max(0, ...numericIds) + 1;
    return `${idPrefix}-${String(nextNumber).padStart(3, "0")}`;
  }, [idPrefix, rows]);

  const openCreateModal = () => {
    setEditingRow(null);
    setFormValues(createEmptyValues(fields));
  };

  const openEditModal = (row) => {
    setEditingRow(row);
    setFormValues(row);
  };

  const closeFormModal = () => {
    setEditingRow(null);
    setFormValues(null);
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormValues((current) => ({ ...current, [name]: value }));
  };

  const saveResource = () => {
    if (editingRow) {
      setRows((current) =>
        current.map((row) =>
          row.id === editingRow.id ? { ...formValues, id: editingRow.id } : row,
        ),
      );
    } else {
      setRows((current) => [...current, { ...formValues, id: nextId }]);
    }

    closeFormModal();
  };

  const deleteResource = () => {
    setRows((current) => current.filter((row) => row.id !== deletingRow.id));
    setDeletingRow(null);
  };

  return {
    rows,
    editingRow,
    deletingRow,
    formValues,
    isEditing: Boolean(editingRow),
    openCreateModal,
    openEditModal,
    closeFormModal,
    setDeletingRow,
    handleChange,
    saveResource,
    deleteResource,
  };
}
