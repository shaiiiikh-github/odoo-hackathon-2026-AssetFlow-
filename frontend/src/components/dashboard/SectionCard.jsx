export default function SectionCard({
  title,
  description,
  children,
  action,
  className = "",
}) {
  return (
    <section
      className={`rounded-[1.5rem] border border-white/80 bg-white p-5 shadow-[0_10px_30px_rgba(15,23,42,0.06)] transition duration-200 sm:p-6 ${className}`}
    >
      {(title || description || action) && (
        <div className="mb-6 flex items-start justify-between gap-4">
          <div className="min-w-0">
            {title && (
              <h2 className="text-base font-semibold tracking-tight text-[#0F172A]">
                {title}
              </h2>
            )}
            {description && (
              <p className="mt-1 text-sm font-medium text-slate-500">
                {description}
              </p>
            )}
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}

      {children}
    </section>
  );
}
