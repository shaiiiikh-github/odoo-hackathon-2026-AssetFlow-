import { X } from "lucide-react";
import { useEffect, useId } from "react";

export default function Modal({ title, description, isOpen, onClose, children }) {
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    if (!isOpen) {
      return undefined;
    }

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Close modal"
        className="absolute inset-0 bg-slate-950/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        className="relative w-full max-w-xl animate-[modal-in_160ms_ease-out] rounded-[1.5rem] border border-white/80 bg-white shadow-[0_30px_80px_rgba(15,23,42,0.24)]"
      >
        <header className="flex items-start justify-between gap-4 border-b border-[#E2E8F0] p-6">
          <div>
            <h2 id={titleId} className="text-lg font-semibold tracking-tight text-[#0F172A]">
              {title}
            </h2>
            {description && (
              <p id={descriptionId} className="mt-1 text-sm font-medium text-slate-500">
                {description}
              </p>
            )}
          </div>
          <button
            type="button"
            aria-label="Close"
            className="flex h-9 w-9 items-center justify-center rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#0F172A]"
            onClick={onClose}
          >
            <X size={18} />
          </button>
        </header>
        <div className="p-6">{children}</div>
      </section>
    </div>
  );
}
