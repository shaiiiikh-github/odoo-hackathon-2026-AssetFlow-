import AdminResourcePage from "../../components/common/AdminResourcePage";
import { categoriesSeed } from "../../constants/adminData";

const columns = [
  { key: "id", label: "ID" },
  { key: "name", label: "Category" },
  { key: "code", label: "Code" },
  { key: "assets", label: "Assets" },
  { key: "status", label: "Status" },
];

const fields = [
  { name: "name", label: "Category Name", placeholder: "Laptops", required: true },
  { name: "code", label: "Category Code", placeholder: "LAP", required: true },
  { name: "assets", label: "Assets", type: "number", placeholder: "128", required: true },
  { name: "status", label: "Status", placeholder: "Active", defaultValue: "Active", required: true },
];

export default function Categories() {
  return (
    <AdminResourcePage
      eyebrow="Admin Module"
      title="Asset Categories"
      description="Maintain reusable asset categories that power registration and reporting."
      entityName="Category"
      idPrefix="CAT"
      rows={categoriesSeed}
      columns={columns}
      fields={fields}
    />
  );
}
