export default function RequestFilters({
  search,
  status,
  priority,
  onSearchChange,
  onStatusChange,
  onPriorityChange,
  showPriority = true,
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-[1.4fr_0.8fr_0.8fr]">
      <label className="block">
        <span className="text-sm font-semibold text-[#0F172A]">Search</span>
        <input
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search requests, employees, assets..."
          className="mt-2 h-11 w-full rounded-2xl border border-[#E2E8F0] bg-white px-4 text-sm font-medium text-[#0F172A] outline-none shadow-sm transition placeholder:text-slate-400 focus:border-[#2563EB] focus:ring-4 focus:ring-blue-100"
        />
      </label>

      <label className="block">
        <span className="text-sm font-semibold text-[#0F172A]">Status</span>
        <select
          value={status}
          onChange={(event) => onStatusChange(event.target.value)}
          className="mt-2 h-11 w-full rounded-2xl border border-[#E2E8F0] bg-white px-4 text-sm font-medium text-[#0F172A] outline-none shadow-sm transition focus:border-[#2563EB] focus:ring-4 focus:ring-blue-100"
        >
          <option value="All">All</option>
          <option value="Pending">Pending</option>
          <option value="Under Review">Under Review</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
          <option value="Allocated">Allocated</option>
          <option value="Completed">Completed</option>
        </select>
      </label>

      {showPriority ? (
        <label className="block">
          <span className="text-sm font-semibold text-[#0F172A]">Priority</span>
          <select
            value={priority}
            onChange={(event) => onPriorityChange(event.target.value)}
            className="mt-2 h-11 w-full rounded-2xl border border-[#E2E8F0] bg-white px-4 text-sm font-medium text-[#0F172A] outline-none shadow-sm transition focus:border-[#2563EB] focus:ring-4 focus:ring-blue-100"
          >
            <option value="All">All</option>
            <option value="Low">Low</option>
            <option value="Medium">Medium</option>
            <option value="High">High</option>
          </select>
        </label>
      ) : (
        <div className="hidden lg:block" />
      )}
    </div>
  );
}