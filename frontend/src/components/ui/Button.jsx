import { cloneElement, isValidElement } from "react";

const variants = {
  primary: "bg-gradient-to-r from-[#2563EB] to-[#1D4ED8] text-white shadow-[0_10px_20px_rgba(37,99,235,0.18)] hover:translate-y-[-1px] hover:shadow-[0_12px_24px_rgba(37,99,235,0.24)] focus-visible:ring-blue-200",
  secondary:
    "border border-[#E2E8F0] bg-white text-[#0F172A] shadow-sm hover:-translate-y-0.5 hover:border-blue-100 hover:bg-slate-50 focus-visible:ring-slate-200",
  danger: "bg-gradient-to-r from-[#EF4444] to-[#DC2626] text-white shadow-[0_10px_20px_rgba(239,68,68,0.18)] hover:translate-y-[-1px] hover:shadow-[0_12px_24px_rgba(239,68,68,0.24)] focus-visible:ring-red-200",
};

export default function Button({
  children,
  asChild = false,
  variant = "primary",
  className = "",
  type = "button",
  ...props
}) {
  const classes = `inline-flex h-10 items-center justify-center gap-2 rounded-2xl px-4 text-sm font-semibold transition duration-200 focus-visible:outline-none focus-visible:ring-4 disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`;

  if (asChild) {
    return isValidElement(children)
      ? cloneElement(children, {
          className: [classes, children.props.className].filter(Boolean).join(" "),
        })
      : null;
  }

  return (
    <button
      type={type}
      className={classes}
      {...props}
    >
      {children}
    </button>
  );
}
