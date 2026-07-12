export default function LoadingState({ rows = 4 }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="space-y-3 rounded-2xl border border-[#E2E8F0] bg-white p-5"
    >
      <span className="sr-only">Loading</span>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="h-12 animate-pulse rounded-2xl bg-slate-100" />
      ))}
    </div>
  );
}
