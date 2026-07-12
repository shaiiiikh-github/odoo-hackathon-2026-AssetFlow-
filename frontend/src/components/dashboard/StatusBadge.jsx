const toneClasses = {
  success: "bg-emerald-50 text-[#15803D] ring-emerald-100",
  warning: "bg-amber-50 text-[#B45309] ring-amber-100",
  danger: "bg-rose-50 text-[#B91C1C] ring-rose-100",
  info: "bg-blue-50 text-[#2563EB] ring-blue-100",
  neutral: "bg-slate-50 text-slate-600 ring-slate-200",
};

export default function StatusBadge({ children, tone = "neutral", dotColor }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ring-1 ${
        toneClasses[tone] || toneClasses.neutral
      }`}
    >
      {dotColor && (
        <span
          className="h-2 w-2 rounded-full"
          style={{ backgroundColor: dotColor }}
        />
      )}
      {children}
    </span>
  );
}
