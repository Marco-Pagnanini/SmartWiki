import { FileText, LoaderCircle, TriangleAlert, X } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface AttachmentChipProps {
  name: string
  status?: "uploading" | "ready" | "error"
  error?: string
  onRemove?: () => void
}

/** A file attached to a message: shown in the composer while uploading and in the sent bubble. */
export function AttachmentChip({ name, status = "ready", error, onRemove }: AttachmentChipProps) {
  const Icon = status === "uploading" ? LoaderCircle : status === "error" ? TriangleAlert : FileText
  return (
    <div
      className={cn(
        "flex max-w-full items-center gap-2.5 rounded-xl border bg-background py-1.5 pr-1.5 pl-2.5 text-sm",
        status === "error" && "border-destructive/40 text-destructive",
      )}
    >
      <span
        className={cn(
          "flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted",
          status === "error" && "bg-destructive/10",
        )}
      >
        <Icon className={cn("size-4", status === "uploading" && "animate-spin")} aria-hidden="true" />
      </span>
      <span className="flex min-w-0 flex-col">
        <span className="truncate font-medium">{name}</span>
        <span className={cn("truncate text-xs text-muted-foreground", status === "error" && "text-destructive/80")}>
          {status === "uploading" ? "Uploading…" : status === "error" ? error : "Attached"}
        </span>
      </span>
      {onRemove && (
        <Button type="button" variant="ghost" size="icon-sm" className="rounded-full" onClick={onRemove} aria-label={`Remove ${name}`}>
          <X />
        </Button>
      )}
    </div>
  )
}
