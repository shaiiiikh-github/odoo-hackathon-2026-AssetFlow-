import StatCard from "./StatCard";

export default function StatsGrid({ items }) {
  return (
    <section className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <StatCard key={item.label} {...item} />
      ))}
    </section>
  );
}
