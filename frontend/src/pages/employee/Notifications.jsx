import NotificationPanel from "../../components/employee/NotificationPanel";
import PageHeader from "../../components/dashboard/PageHeader";
import useAuth from "../../hooks/useAuth";
import useAssetRequests from "../../hooks/useAssetRequests";

export default function Notifications() {
  const { user, role } = useAuth();
  const requestApi = useAssetRequests();
  const notifications = requestApi.getNotificationsForUser(role, user.email);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Employee"
        title="Notifications"
        description="Review allocation, maintenance, return, and policy updates."
      />

      <NotificationPanel notifications={notifications} />
    </div>
  );
}
