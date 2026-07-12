export default function PageHeader({
  eyebrow,
  title,
  description,
  action,
  children,
}) {
  return (
    <section className="overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm sm:p-8">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-3xl">
          {eyebrow && (
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#2563EB]">
              {eyebrow}
            </p>
          )}
          <h1 className="mt-3 text-2xl font-semibold tracking-tight text-[#1E293B] sm:text-4xl">
            {title}
          </h1>
          {description && (
            <p className="mt-3 max-w-2xl text-base font-medium leading-7 text-slate-500">
              {description}
            </p>
          )}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
