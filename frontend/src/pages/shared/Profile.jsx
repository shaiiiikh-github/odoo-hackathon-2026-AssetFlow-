import PageHeader from "../../components/dashboard/PageHeader";
import SectionCard from "../../components/dashboard/SectionCard";
import { getCurrentUser } from "../../utils/authMock";

export default function Profile() {
  const user = getCurrentUser();

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Shared"
        title="Profile"
        description="Basic mock profile details. This is ready to connect to authenticated backend user data."
      />
      <SectionCard title="Current User" description="Mock session identity">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#2563EB] text-base font-semibold text-white">
            {user.initials}
          </div>
          <div>
            <p className="text-sm font-semibold text-[#1E293B]">{user.name}</p>
            <p className="mt-1 text-sm font-medium text-slate-500">{user.role}</p>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
