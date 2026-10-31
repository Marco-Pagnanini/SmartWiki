import { useEffect, useRef, useState } from "react"

import { AppHeader } from "@/components/app-header"
import { ChatComposer } from "@/components/chat-composer"
import { ChatMessage } from "@/components/chat-message"
import { PacketFlow } from "@/components/packet-flow"
import { Button } from "@/components/ui/button"
import { TooltipProvider } from "@/components/ui/tooltip"
import { sendMessage, type Message, type UploadedAttachment } from "@/lib/chat"

const SUGGESTIONS = ["What can you do?", "Find the document manuale-ferie.pdf", "Add a document to group 3"]

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [working, setWorking] = useState(false)
  // The answer waits here until the packet animation has finished its cycle
  const [result, setResult] = useState<Message | null>(null)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end", behavior: "smooth" })
  }, [messages, working])

  async function send(text: string, attachment?: UploadedAttachment) {
    const history = messages
    setMessages([...history, { role: "user", content: text, attachment }])
    setResult(null)
    setWorking(true)
    try {
      const reply = await sendMessage(text, history, attachment?.attachment_id)
      setResult({ role: "assistant", content: reply })
    } catch (e) {
      const detail = e instanceof Error ? e.message : "Unknown error"
      setResult({ role: "assistant", content: detail, error: true })
    }
  }

  function showResult() {
    if (result) setMessages((prev) => [...prev, result])
    setResult(null)
    setWorking(false)
  }

  const empty = messages.length === 0 && !working

  return (
    <TooltipProvider>
      <div className="flex h-dvh flex-col">
        <AppHeader canReset={messages.length > 0 && !working} onReset={() => setMessages([])} />

        {empty ? (
          <main className="flex flex-1 flex-col items-center justify-center px-4 pb-[10vh]">
            <div className="w-full max-w-3xl">
              <h1 className="mb-7 text-center text-2xl font-semibold tracking-tight text-balance sm:text-3xl">
                What can I help with?
              </h1>
              <ChatComposer disabled={working} onSend={send} />
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <Button key={s} variant="outline" className="rounded-full px-4 text-muted-foreground" onClick={() => send(s)}>
                    {s}
                  </Button>
                ))}
              </div>
            </div>
          </main>
        ) : (
          <>
            <main className="flex-1 overflow-y-auto">
              <div className="mx-auto flex max-w-3xl flex-col gap-8 px-4 pt-4 pb-10">
                {messages.map((m, i) => (
                  <ChatMessage key={i} message={m} />
                ))}
                {working && <PacketFlow done={result !== null} onFinish={showResult} />}
                <div ref={endRef} />
              </div>
            </main>
            <div className="mx-auto w-full max-w-3xl px-4 pb-3">
              <ChatComposer disabled={working} onSend={send} />
              <p className="mt-2 text-center text-xs text-muted-foreground">
                The agents can make mistakes. Check important details.
              </p>
            </div>
          </>
        )}
      </div>
    </TooltipProvider>
  )
}
