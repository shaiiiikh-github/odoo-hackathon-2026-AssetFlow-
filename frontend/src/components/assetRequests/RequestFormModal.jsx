import { useMemo, useState } from "react";
import {
  BadgeCheck,
  ChevronLeft,
  ChevronRight,
  FileText,
  Keyboard,
  Laptop,
  Layers3,
  Monitor,
  Mouse,
  Printer,
  Sparkles,
  PackageSearch,
  Headphones,
} from "lucide-react";
import { requestCategories, requestPriorities } from "../../services/assetRequestService";
import Button from "../ui/Button";
import Input from "../ui/Input";
import Modal from "../ui/Modal";

const initialValues = {
  assetCategory: "Laptop",
  reason: "",
  priority: "Medium",
  requiredBy: "",
  businessJustification: "",
  notes: "",
  attachments: [],
};

export default function RequestFormModal({
  isOpen,
  onClose,
  onSubmit,
  requestCount = 0,
  isSubmitting = false,
}) {
  const [values, setValues] = useState(initialValues);
  const [step, setStep] = useState(1);
  const [isAdditionalOpen, setIsAdditionalOpen] = useState(false);
  const [submissionSummary, setSubmissionSummary] = useState(null);

  function handleChange(event) {
    const { name, value, files } = event.target;

    if (name === "attachments") {
      setValues((current) => ({
        ...current,
        attachments: Array.from(files || []).map((file) => file.name),
      }));
      return;
    }

    setValues((current) => ({ ...current, [name]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();

    if (step < 3) {
      return;
    }

    onSubmit(values);
    setSubmissionSummary({
      requestId: `REQ-${String(2400 + requestCount + 1)}`,
      status: "Pending",
      expectedReviewTime: getExpectedReviewTime(values.priority),
    });
  }

  const selectedCategory = useMemo(
    () => requestCategories.find((category) => category === values.assetCategory) || requestCategories[0],
    [values.assetCategory],
  );

  const modalTitle = submissionSummary
    ? "Request Submitted"
    : step === 1
      ? "Request New Asset"
      : step === 2
        ? "Request Details"
        : "Review Request";

  const modalDescription = submissionSummary
    ? "Your request is now in the review queue."
    : step === 1
      ? "Choose an asset category and continue through the streamlined request flow."
      : step === 2
        ? "Keep the form focused on the essentials."
        : "Confirm the details before submitting to your manager.";

  return (
    <Modal isOpen={isOpen} title={modalTitle} description={modalDescription} onClose={onClose}>
      {submissionSummary ? (
        <SuccessState summary={submissionSummary} onViewRequests={onClose} />
      ) : (
        <form className="space-y-6" onSubmit={handleSubmit}>
          <WizardProgress step={step} />

          {step === 1 && (
            <section className="space-y-5">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#2563EB]">Step 1</p>
                <h3 className="mt-2 text-2xl font-semibold tracking-tight text-[#0F172A]">Choose Asset Category</h3>
                <p className="mt-2 max-w-2xl text-sm font-medium leading-6 text-slate-500">
                  Select the asset type as a modern card instead of a dropdown.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {requestCategories.map((category) => (
                  <CategoryCard
                    key={category}
                    category={category}
                    selected={values.assetCategory === category}
                    onClick={() => setValues((current) => ({ ...current, assetCategory: category }))}
                  />
                ))}
              </div>

              <div className="flex items-center justify-between pt-2">
                <Button variant="secondary" onClick={onClose}>
                  Cancel
                </Button>
                <Button type="button" onClick={() => setStep(2)}>
                  Continue
                  <ChevronRight size={16} />
                </Button>
              </div>
            </section>
          )}

          {step === 2 && (
            <section className="space-y-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#2563EB]">Step 2</p>
                  <h3 className="mt-2 text-2xl font-semibold tracking-tight text-[#0F172A]">Essential Details</h3>
                  <p className="mt-2 max-w-2xl text-sm font-medium leading-6 text-slate-500">
                    Keep the form focused on the fields that matter most.
                  </p>
                </div>
                <SelectedCategoryPill category={selectedCategory} />
              </div>

              <div className="grid gap-5">
                <Input
                  label="Reason"
                  name="reason"
                  type="textarea"
                  placeholder="Explain why this asset is required"
                  value={values.reason}
                  onChange={handleChange}
                  required
                />

                <div className="grid gap-5 md:grid-cols-2">
                  <SelectField
                    label="Priority"
                    name="priority"
                    value={values.priority}
                    onChange={handleChange}
                    options={requestPriorities}
                  />

                  <Input
                    label="Required By"
                    name="requiredBy"
                    type="date"
                    value={values.requiredBy}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <Button variant="secondary" type="button" onClick={() => setStep(1)}>
                  <ChevronLeft size={16} />
                  Back
                </Button>
                <Button type="button" onClick={() => setStep(3)}>
                  Review Request
                  <ChevronRight size={16} />
                </Button>
              </div>
            </section>
          )}

          {step === 3 && (
            <section className="space-y-6">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.18em] text-[#2563EB]">Step 3</p>
                <h3 className="mt-2 text-2xl font-semibold tracking-tight text-[#0F172A]">Review Request</h3>
                <p className="mt-2 max-w-2xl text-sm font-medium leading-6 text-slate-500">
                  Confirm the request summary before submission.
                </p>
              </div>

              <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
                <div className="rounded-[1.5rem] border border-white/80 bg-white p-6 shadow-[0_10px_30px_rgba(15,23,42,0.06)]">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">Asset</p>
                      <p className="mt-2 text-xl font-semibold tracking-tight text-[#0F172A]">{values.assetCategory}</p>
                    </div>
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-[#2563EB] ring-1 ring-blue-100">
                      <PackageSearch size={20} />
                    </div>
                  </div>

                  <div className="mt-6 grid gap-4 sm:grid-cols-3">
                    <ReviewStat label="Priority" value={values.priority} />
                    <ReviewStat label="Required Date" value={values.requiredBy || "Not set"} />
                    <ReviewStat label="Reason" value={values.reason || "Not added"} />
                  </div>
                </div>

                <div className="rounded-[1.5rem] border border-[#E2E8F0] bg-[#F8FAFC] p-5 shadow-sm">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Additional Information</p>
                      <p className="mt-2 text-sm font-semibold text-[#0F172A]">Business Justification, Notes and Attachments</p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setIsAdditionalOpen((current) => !current)}
                      className="flex h-10 w-10 items-center justify-center rounded-2xl border border-[#E2E8F0] bg-white text-slate-500 shadow-sm"
                    >
                      <ChevronRight size={16} className={`transition ${isAdditionalOpen ? "rotate-90" : ""}`} />
                    </button>
                  </div>

                  {isAdditionalOpen && (
                    <div className="mt-4 space-y-4">
                      <Input
                        label="Business Justification"
                        name="businessJustification"
                        type="textarea"
                        placeholder="Describe the business outcome this asset supports"
                        value={values.businessJustification}
                        onChange={handleChange}
                      />
                      <Input
                        label="Notes"
                        name="notes"
                        type="textarea"
                        placeholder="Optional notes for the manager"
                        value={values.notes}
                        onChange={handleChange}
                      />
                      <label className="block">
                        <span className="text-sm font-semibold text-[#0F172A]">Attachments</span>
                        <div className="mt-2 rounded-2xl border border-dashed border-[#CBD5E1] bg-white p-4 shadow-sm">
                          <input
                            name="attachments"
                            type="file"
                            multiple
                            onChange={handleChange}
                            className="block w-full text-sm text-slate-500 file:mr-4 file:rounded-xl file:border-0 file:bg-blue-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-[#2563EB]"
                          />
                          <p className="mt-3 text-xs font-medium text-slate-400">
                            {values.attachments.length
                              ? `${values.attachments.length} file(s) selected`
                              : "Optional supporting documents"}
                          </p>
                        </div>
                      </label>
                    </div>
                  )}
                </div>
              </div>

              <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-between">
                <Button variant="secondary" type="button" onClick={() => setStep(2)}>
                  <ChevronLeft size={16} />
                  Back
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Submitting..." : "Submit Request"}
                  <ChevronRight size={16} />
                </Button>
              </div>
            </section>
          )}
        </form>
      )}
    </Modal>
  );
}

function SelectField({ label, name, value, onChange, options }) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-[#0F172A]">{label}</span>
      <select
        name={name}
        value={value}
        onChange={onChange}
        className="mt-2 h-11 w-full rounded-2xl border border-[#E2E8F0] bg-white px-4 text-sm font-medium text-[#0F172A] outline-none shadow-sm transition duration-200 focus:border-[#2563EB] focus:ring-4 focus:ring-blue-100"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function WizardProgress({ step }) {
  const items = ["Category", "Details", "Review"];

  return (
    <div className="grid gap-3 sm:grid-cols-3">
      {items.map((item, index) => {
        const currentStep = index + 1;
        const isActive = currentStep === step;
        const isComplete = currentStep < step;

        return (
          <div
            key={item}
            className={`rounded-2xl border px-4 py-3 ${
              isActive
                ? "border-blue-200 bg-blue-50"
                : isComplete
                  ? "border-emerald-100 bg-emerald-50"
                  : "border-[#E2E8F0] bg-white"
            }`}
          >
            <div className="flex items-center gap-3">
              <span
                className={`flex h-9 w-9 items-center justify-center rounded-xl text-sm font-semibold ${
                  isActive
                    ? "bg-[#2563EB] text-white"
                    : isComplete
                      ? "bg-emerald-500 text-white"
                      : "bg-slate-100 text-slate-500"
                }`}
              >
                {currentStep}
              </span>
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Step {currentStep}</p>
                <p className="mt-1 text-sm font-semibold text-[#0F172A]">{item}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CategoryCard({ category, selected, onClick }) {
  const Icon = categoryIcons[category] || Layers3;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`group flex items-start gap-4 rounded-[1.25rem] border p-4 text-left transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_12px_24px_rgba(37,99,235,0.08)] ${
        selected
          ? "border-[#2563EB] bg-blue-50 shadow-[0_12px_24px_rgba(37,99,235,0.08)]"
          : "border-[#E2E8F0] bg-white"
      }`}
    >
      <span
        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${
          selected ? "bg-[#2563EB] text-white" : "bg-blue-50 text-[#2563EB]"
        }`}
      >
        <Icon size={20} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block text-sm font-semibold text-[#0F172A]">{category}</span>
        <span className="mt-1 block text-xs font-medium text-slate-500">Tap to select and continue</span>
      </span>
      {selected && <Sparkles size={16} className="mt-1 text-[#2563EB]" />}
    </button>
  );
}

function SelectedCategoryPill({ category }) {
  const Icon = categoryIcons[category] || Layers3;

  return (
    <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-4 py-2 text-sm font-semibold text-[#2563EB] ring-1 ring-blue-100">
      <Icon size={16} />
      {category}
    </div>
  );
}

function ReviewStat({ label, value }) {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-[#F8FAFC] p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 text-sm font-semibold text-[#0F172A]">{value}</p>
    </div>
  );
}

function SuccessState({ summary, onViewRequests }) {
  return (
    <div className="space-y-6">
      <div className="rounded-[1.5rem] border border-emerald-100 bg-gradient-to-br from-emerald-50 via-white to-white p-6 shadow-[0_18px_40px_rgba(16,185,129,0.10)]">
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500 text-white shadow-lg shadow-emerald-500/20">
            <BadgeCheck size={26} />
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-emerald-600">Submitted successfully</p>
            <h3 className="mt-2 text-2xl font-semibold tracking-tight text-[#0F172A]">Your request is in review</h3>
            <p className="mt-2 text-sm font-medium leading-6 text-slate-500">
              The request has been created and sent to the manager workflow.
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <ResultCard label="Request ID" value={summary.requestId} />
          <ResultCard label="Status" value={summary.status} />
          <ResultCard label="Expected Review Time" value={summary.expectedReviewTime} />
        </div>
      </div>

      <div className="flex justify-end">
        <Button onClick={onViewRequests}>
          View My Requests
          <ChevronRight size={16} />
        </Button>
      </div>
    </div>
  );
}

function ResultCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/80 bg-white p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 text-sm font-semibold text-[#0F172A]">{value}</p>
    </div>
  );
}

function getExpectedReviewTime(priority) {
  if (priority === "High") {
    return "Within 1 business day";
  }

  if (priority === "Medium") {
    return "Within 1-2 business days";
  }

  return "Within 2 business days";
}

const categoryIcons = {
  Laptop,
  Desktop: Monitor,
  Monitor,
  Keyboard,
  Mouse,
  "Docking Station": Layers3,
  Printer,
  Projector: Monitor,
  Headset: Headphones,
  "Software License": FileText,
};