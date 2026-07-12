export default function SectionCard({
  title,
  description,
  children,
  action,
  className = "",
}) {
  return (
    <section
      className={`rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm transition duration-200 sm:p-6 ${className}`}
    >
      {(title || description || action) && (
        <div className="mb-6 flex items-start justify-between gap-4">
          <div className="min-w-0">
            {title && (
              <h2 className="text-base font-semibold text-[#1E293B]">
                {title}
              </h2>
            )}
            {description && (
              <p className="mt-1 text-sm font-medium text-slate-500">
                {description}
              </p>
            )}
          </div>
          {action}
        </div>
      )}

      {children}
    </section>
  );
}
