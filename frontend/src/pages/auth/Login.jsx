import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import Button from "../../components/ui/Button";

export default function Login() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#F8FAFC] p-4">
      <section className="w-full max-w-md rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm sm:p-8">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#2563EB]">
            AssetFlow Pro
          </p>
          <h1 className="mt-3 text-2xl font-semibold text-[#1E293B]">
            Smart Enterprise Asset Management
          </h1>
          <p className="mt-3 text-sm font-medium leading-6 text-slate-500">
            Mock login shortcuts are available until backend authentication is
            connected.
          </p>
        </div>

        <div className="mt-6 grid gap-3">
          <LoginLink to="/admin" label="Continue as Admin" />
          <LoginLink to="/manager" label="Continue as Asset Manager" />
          <LoginLink to="/employee" label="Continue as Employee" />
        </div>
      </section>
    </main>
  );
}

function LoginLink({ to, label }) {
  return (
    <Button asChild className="w-full justify-between">
      <Link to={to}>
        {label}
        <ArrowRight size={18} />
      </Link>
    </Button>
  );
}
