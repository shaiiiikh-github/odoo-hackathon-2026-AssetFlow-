import { cloneElement, isValidElement } from "react";

const variants = {
  primary: "bg-[#2563EB] text-white hover:bg-blue-700 focus-visible:ring-blue-200",
  secondary:
    "border border-[#E2E8F0] bg-white text-[#1E293B] hover:bg-slate-50 focus-visible:ring-slate-200",
  danger: "bg-[#EF4444] text-white hover:bg-red-600 focus-visible:ring-red-200",
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
