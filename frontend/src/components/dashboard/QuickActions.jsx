import QuickActionCard from "./QuickActionCard";
import SectionCard from "./SectionCard";

export default function QuickActions({ items }) {
  return (
    <SectionCard title="Quick Actions" description="Common manager workflows">
      <div className="grid gap-3 sm:grid-cols-2">
        {items.map((item) => (
          <QuickActionCard key={item.title} {...item} />
        ))}
      </div>
    </SectionCard>
  );
}
