import SectionCard from "./SectionCard";

export default function ChartCard({ title, description, children, footer }) {
  return (
    <SectionCard title={title} description={description}>
      <div className="h-80 rounded-2xl bg-gradient-to-b from-slate-50 to-white p-2 ring-1 ring-slate-100">
        {children}
      </div>
      {footer && <div className="mt-4">{footer}</div>}
    </SectionCard>
  );
}
