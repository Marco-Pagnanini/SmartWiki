import { ArrowUp, Paperclip } from "lucide-react"
import { useRef, useState, type ChangeEvent, type FormEvent, type KeyboardEvent } from "react"

import { AttachmentChip } from "@/components/attachment-chip"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { uploadAttachment, type UploadedAttachment } from "@/lib/chat"

const ACCEPTED_FILES = ".pdf,.txt,.md"

type PendingFile =
  | { status: "uploading"; name: string }
  | { status: "ready"; name: string; uploaded: UploadedAttachment }
  | { status: "error"; name: string; error: string }

interface ChatComposerProps {
  disabled: boolean
  onSend: (text: string, attachment?: UploadedAttachment) => void
}

export function ChatComposer({ disabled, onSend }: ChatComposerProps) {
  const [text, setText] = useState("")
  const [file, setFile] = useState<PendingFile | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)
  // A file still uploading or rejected blocks sending: the message would lose its attachment
  const canSend = text.trim().length > 0 && !disabled && (file === null || file.status === "ready")

  async function handleFile(e: ChangeEvent<HTMLInputElement>) {
    const picked = e.target.files?.[0]
    e.target.value = "" // lets the user pick the same file again
    if (!picked) return
    // The file is uploaded right away, so a wrong file is reported before the message is written
    setFile({ status: "uploading", name: picked.name })
    try {
      const uploaded = await uploadAttachment(picked)
      setFile({ status: "ready", name: uploaded.filename, uploaded })
    } catch (err) {
      setFile({ status: "error", name: picked.name, error: err instanceof Error ? err.message : "Upload failed" })
    }
  }

  function submit(e?: FormEvent) {
    e?.preventDefault()
    if (!canSend) return
    onSend(text.trim(), file?.status === "ready" ? file.uploaded : undefined)
    setText("")
    setFile(null)
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends, Shift+Enter starts a new line
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <form
      onSubmit={submit}
      className="flex flex-col rounded-3xl border bg-background p-2 shadow-sm transition-[border-color,box-shadow] focus-within:border-ring focus-within:ring-3 focus-within:ring-ring/30 dark:bg-muted/40"
    >
      {file && (
        <div className="flex px-1 pt-1">
          <AttachmentChip
            name={file.name}
            status={file.status}
            error={file.status === "error" ? file.error : undefined}
            onRemove={file.status === "uploading" ? undefined : () => setFile(null)}
          />
        </div>
      )}
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={file ? "Tell the agents what to do with this file" : "Ask the wiki agents anything"}
        aria-label="Message"
        rows={1}
        autoFocus
        className="max-h-52 min-h-11 resize-none border-0 bg-transparent px-3 py-2.5 text-base shadow-none focus-visible:ring-0 md:text-base dark:bg-transparent"
      />
      <div className="flex items-center justify-between">
        <input ref={fileInput} type="file" accept={ACCEPTED_FILES} className="hidden" onChange={handleFile} />
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="rounded-full"
              onClick={() => fileInput.current?.click()}
              disabled={disabled || file?.status === "uploading"}
              aria-label="Attach a file"
            >
              <Paperclip className="size-5" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Attach a PDF, TXT or MD file</TooltipContent>
        </Tooltip>
        <Button type="submit" size="icon" className="rounded-full" disabled={!canSend} aria-label="Send message">
          <ArrowUp className="size-5" />
        </Button>
      </div>
    </form>
  )
}
