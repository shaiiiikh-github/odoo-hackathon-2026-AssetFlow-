import AdminResourcePage from "../../components/common/AdminResourcePage";
import { departmentsSeed } from "../../constants/adminData";

const columns = [
  { key: "id", label: "ID" },
  { key: "name", label: "Department" },
  { key: "head", label: "Head" },
  { key: "employees", label: "Employees" },
  { key: "status", label: "Status" },
];

const fields = [
  { name: "name", label: "Department Name", placeholder: "Engineering", required: true },
  { name: "head", label: "Department Head", placeholder: "Neha Kapoor", required: true },
  { name: "employees", label: "Employees", type: "number", placeholder: "42", required: true },
  { name: "status", label: "Status", placeholder: "Active", defaultValue: "Active", required: true },
];

export default function Departments() {
  return (
    <AdminResourcePage
      eyebrow="Admin Module"
      title="Departments"
      description="Create, edit, and organize company departments for asset ownership."
      entityName="Department"
      idPrefix="DEP"
      rows={departmentsSeed}
      columns={columns}
      fields={fields}
    />
  );
}
