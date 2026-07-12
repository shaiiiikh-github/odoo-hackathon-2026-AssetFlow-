import { X } from "lucide-react";
import { useEffect, useId } from "react";

const modalSizes = {
  sm: "max-w-lg",
  md: "max-w-2xl",
  lg: "max-w-4xl",
  xl: "max-w-6xl",
};

export default function Modal({
  title,
  description,
  isOpen,
  onClose,
  children,
  size = "md",
}) {
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.body.style.overflow = "hidden";

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = "";
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/50 p-6 backdrop-blur-md">
      {/* Overlay */}
      <button
        type="button"
        aria-label="Close"
        className="absolute inset-0 cursor-default"
        onClick={onClose}
      />

      {/* Modal */}
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        className={`relative w-full ${modalSizes[size]} max-h-[92vh] overflow-hidden rounded-[28px] bg-white shadow-[0_30px_80px_rgba(15,23,42,0.25)] ring-1 ring-slate-200 animate-[modal-in_180ms_ease-out]`}
      >
        {/* Header */}
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
          <div className="flex items-start justify-between px-8 py-6">
            <div className="max-w-3xl">
              <h2
                id={titleId}
                className="text-2xl font-bold tracking-tight text-slate-900"
              >
                {title}
              </h2>

              {description && (
                <p
                  id={descriptionId}
                  className="mt-2 text-sm leading-6 text-slate-500"
                >
                  {description}
                </p>
              )}
            </div>

            <button
              onClick={onClose}
              className="flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-white transition-all hover:bg-slate-100 hover:shadow"
            >
              <X size={20} />
            </button>
          </div>
        </header>

        {/* Scrollable Body */}
        <div className="max-h-[calc(92vh-105px)] overflow-y-auto bg-slate-50 px-8 py-8">
          {children}
        </div>
      </section>
    </div>
  );
}