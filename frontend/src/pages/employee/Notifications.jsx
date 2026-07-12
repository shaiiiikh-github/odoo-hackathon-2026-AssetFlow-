import NotificationPanel from "../../components/employee/NotificationPanel";
import PageHeader from "../../components/dashboard/PageHeader";
import { employeeNotifications } from "../../constants/employeeData";

export default function Notifications() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Employee"
        title="Notifications"
        description="Review allocation, maintenance, return, and policy updates."
      />

      <NotificationPanel notifications={employeeNotifications} />
    </div>
  );
}
