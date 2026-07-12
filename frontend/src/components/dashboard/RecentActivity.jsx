import ActivityCard from "./ActivityCard";
import SectionCard from "./SectionCard";

export default function RecentActivity({ items }) {
  return (
    <SectionCard title="Recent Activity" description="Latest asset operations">
      <ol className="space-y-5">
        {items.map((item, index) => (
          <ActivityCard
            key={item.title}
            {...item}
            index={index}
            isLast={index === items.length - 1}
          />
        ))}
      </ol>
    </SectionCard>
  );
}
