import { ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import Button from "../../components/ui/Button";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <section className="w-full max-w-xl rounded-2xl border border-[#E2E8F0] bg-white p-8 text-center shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#2563EB]">
          404
        </p>
        <h1 className="mt-3 text-2xl font-semibold text-[#1E293B]">
          Page not found
        </h1>
        <p className="mt-3 text-sm font-medium leading-6 text-slate-500">
          The page may not exist or your current role may not have access to it.
        </p>
        <Button asChild className="mt-6">
          <Link to="/">
            <ArrowLeft size={18} />
            Back to login
          </Link>
        </Button>
      </section>
    </div>
  );
}
