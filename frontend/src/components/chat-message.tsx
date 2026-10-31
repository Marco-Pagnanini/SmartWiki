import { TriangleAlert } from "lucide-react"

import { AttachmentChip } from "@/components/attachment-chip"
import { Markdown } from "@/components/markdown"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import type { Message } from "@/lib/chat"

export function ChatMessage({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex flex-col items-end gap-2">
        {message.attachment && <AttachmentChip name={message.attachment.filename} />}
        <div className="max-w-[80%] rounded-3xl bg-muted px-5 py-2.5 leading-7 whitespace-pre-wrap [overflow-wrap:anywhere]">
          {message.content}
        </div>
      </div>
    )
  }

  if (message.error) {
    return (
      <Alert variant="destructive">
        <TriangleAlert />
        <AlertTitle>The agents could not answer</AlertTitle>
        <AlertDescription>{message.content}</AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="animate-in leading-7 duration-500 fade-in slide-in-from-bottom-1 [overflow-wrap:anywhere]">
      <Markdown>{message.content}</Markdown>
    </div>
  )
}
