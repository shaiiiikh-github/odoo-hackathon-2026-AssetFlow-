import SectionCard from "./SectionCard";

export default function ChartCard({ title, description, children, footer }) {
  return (
    <SectionCard title={title} description={description}>
      <div className="h-80">{children}</div>
      {footer && <div className="mt-4">{footer}</div>}
    </SectionCard>
  );
}
