export default function PageHeader({
  eyebrow,
  title,
  description,
  action,
  children,
}) {
  return (
    <section className="relative overflow-hidden rounded-[1.5rem] border border-white/80 bg-white p-6 shadow-[0_10px_30px_rgba(15,23,42,0.06)] sm:p-8">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-200 to-transparent" />
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-3xl">
          {eyebrow && (
            <p className="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[#2563EB] ring-1 ring-blue-100">
              {eyebrow}
            </p>
          )}
          <h1 className="mt-4 text-2xl font-semibold tracking-tight text-[#0F172A] sm:text-4xl">
            {title}
          </h1>
          {description && (
            <p className="mt-3 max-w-2xl text-base font-medium leading-7 text-slate-500">
              {description}
            </p>
          )}
        </div>
        {action && <div className="shrink-0">{action}</div>}
      </div>
      {children}
    </section>
  );
}
