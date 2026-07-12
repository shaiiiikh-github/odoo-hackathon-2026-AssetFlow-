import { useId } from "react";

export default function Input({ label, error, className = "", ...props }) {
  const generatedId = useId();
  const inputId = props.id || `${props.name || "field"}-${generatedId}`;
  const errorId = `${inputId}-error`;
  const Component = props.type === "textarea" ? "textarea" : "input";
  const inputProps = { ...props };

  if (inputProps.type === "textarea") {
    delete inputProps.type;
  }

  return (
    <label className="block">
      <span className="text-sm font-semibold text-[#0F172A]">{label}</span>
      <Component
        id={inputId}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? errorId : undefined}
        className={`mt-2 w-full rounded-2xl border bg-white px-4 text-sm font-medium text-[#0F172A] outline-none transition duration-200 placeholder:text-slate-400 shadow-sm focus:ring-4 ${
          error
            ? "border-[#EF4444] focus:border-[#EF4444] focus:ring-red-100"
            : "border-[#E2E8F0] focus:border-[#2563EB] focus:ring-blue-100"
        } ${
          Component === "textarea" ? "min-h-28 py-3" : "h-11"
        } ${className}`}
        {...inputProps}
      />
      {error && (
        <p id={errorId} className="mt-2 text-sm font-medium text-[#EF4444]">
          {error}
        </p>
      )}
    </label>
  );
}
