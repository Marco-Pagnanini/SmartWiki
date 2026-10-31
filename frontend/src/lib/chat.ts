export type Role = "user" | "assistant"

export interface Message {
  role: Role
  content: string
  /** File sent with this message, if any. */
  attachment?: UploadedAttachment
  error?: boolean
}

export interface UploadedAttachment {
  attachment_id: string
  filename: string
}

async function readJson(res: Response) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : `Request failed (${res.status})`)
  }
  return data
}

/** Uploads a file: the backend extracts its text and returns the id the agents will use. */
export async function uploadAttachment(file: File): Promise<UploadedAttachment> {
  const form = new FormData()
  form.append("file", file)
  // No Content-Type header: the browser sets multipart/form-data with its boundary
  return readJson(await fetch("/api/attachments", { method: "POST", body: form }))
}

/** Sends the new message plus the previous turns to the backend and returns the reply. */
export async function sendMessage(message: string, history: Message[], attachmentId?: string): Promise<string> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      // Failed turns are only shown in the UI: the agents never see them
      // Each turn keeps its attachment id, so the agents can still use that file in later turns
      history: history
        .filter((m) => !m.error)
        .map(({ role, content, attachment }) => ({ role, content, attachment_id: attachment?.attachment_id })),
      attachment_id: attachmentId,
    }),
  })
  const data = await readJson(res)
  return data.reply
}
