import { AlertTriangle } from "lucide-react";
import Button from "../ui/Button";

export default function ErrorState({
  title = "Something went wrong",
  description = "Please try again or refresh the page.",
  onRetry,
}) {
  return (
    <div
      role="alert"
      className="rounded-2xl border border-red-100 bg-red-50 p-5"
    >
      <div className="flex gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white text-[#EF4444]">
          <AlertTriangle size={19} />
        </span>
        <div className="min-w-0">
          <h3 className="text-sm font-semibold text-[#1E293B]">{title}</h3>
          <p className="mt-1 text-sm font-medium leading-6 text-slate-600">
            {description}
          </p>
          {onRetry && (
            <Button className="mt-4" variant="secondary" onClick={onRetry}>
              Retry
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
