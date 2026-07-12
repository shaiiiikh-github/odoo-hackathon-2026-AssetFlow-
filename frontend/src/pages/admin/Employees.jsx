import AdminResourcePage from "../../components/common/AdminResourcePage";
import { employeesSeed } from "../../constants/adminData";

const columns = [
  { key: "id", label: "ID" },
  { key: "name", label: "Employee" },
  { key: "email", label: "Email" },
  { key: "department", label: "Department" },
  { key: "role", label: "Role" },
  { key: "status", label: "Status" },
];

const fields = [
  { name: "name", label: "Employee Name", placeholder: "Anika Rao", required: true },
  { name: "email", label: "Email", type: "email", placeholder: "anika@company.com", required: true },
  { name: "department", label: "Department", placeholder: "Engineering", required: true },
  { name: "role", label: "Role", placeholder: "Employee or Asset Manager", defaultValue: "Employee", required: true },
  { name: "status", label: "Status", placeholder: "Active", defaultValue: "Active", required: true },
];

export default function Employees() {
  return (
    <AdminResourcePage
      eyebrow="Admin Module"
      title="Employees"
      description="Create employees, update assignments, and promote employees to Asset Manager."
      entityName="Employee"
      idPrefix="EMP"
      rows={employeesSeed}
      columns={columns}
      fields={fields}
    />
  );
}
