import Button from "../ui/Button";
import Input from "../ui/Input";

export default function ResourceForm({
  fields,
  values,
  onChange,
  onSubmit,
  onCancel,
  submitLabel,
  isSubmitting = false,
}) {
  return (
    <form className="space-y-5" onSubmit={onSubmit}>
      <div className="grid gap-4 sm:grid-cols-2">
        {fields.map((field) => (
          <Input
            key={field.name}
            label={field.label}
            name={field.name}
            type={field.type || "text"}
            placeholder={field.placeholder}
            value={values[field.name] ?? ""}
            onChange={onChange}
            required={field.required}
            error={field.error}
          />
        ))}
      </div>

      <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}
