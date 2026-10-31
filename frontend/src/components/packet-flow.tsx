import { Bot, ChevronLeft, ChevronRight, Package, Plug, Server, User, Workflow, type LucideIcon } from "lucide-react"
import { Fragment, useEffect, useRef, useState } from "react"

import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface FlowNode {
  label: string
  detail?: string
  icon: LucideIcon
}

// The path of a request through the backend, from left to right
const NODES: FlowNode[] = [
  { label: "You", icon: User },
  { label: "Orchestrator", icon: Workflow },
  { label: "Sub agent", icon: Bot },
  { label: "Tool gateway", detail: "MCP", icon: Plug },
  { label: "Service", detail: "Database", icon: Server },
]

const HOP_MS = 650 // packet travelling between two nodes
const STAY_MS = 450 // packet inside a node

type Direction = "out" | "back"
type Step = { kind: "hop"; lane: number; direction: Direction } | { kind: "stay"; node: number }

// One full cycle: out on the top lane up to the service, back on the bottom lane to the user
const CYCLE: Step[] = (() => {
  const steps: Step[] = []
  const last = NODES.length - 1
  for (let i = 0; i < last; i++) steps.push({ kind: "hop", lane: i, direction: "out" }, { kind: "stay", node: i + 1 })
  for (let i = last - 1; i >= 0; i--) steps.push({ kind: "hop", lane: i, direction: "back" }, { kind: "stay", node: i })
  return steps
})()

interface PacketFlowProps {
  /** True once the real answer has arrived. */
  done: boolean
  /** Called at the end of the first full cycle after `done` became true. */
  onFinish: () => void
}

/**
 * Illustrative loading state: a packet travels through the system while the agents work.
 * It is not driven by the backend; it always completes at least one full cycle.
 */
export function PacketFlow({ done, onFinish }: PacketFlowProps) {
  const [index, setIndex] = useState(0)
  const doneRef = useRef(done)
  const finishRef = useRef(onFinish)

  useEffect(() => {
    doneRef.current = done
    finishRef.current = onFinish
  })

  useEffect(() => {
    const step = CYCLE[index]
    const timer = setTimeout(
      () => {
        if (index < CYCLE.length - 1) setIndex(index + 1)
        else if (doneRef.current) finishRef.current()
        else setIndex(0)
      },
      step.kind === "hop" ? HOP_MS : STAY_MS,
    )
    return () => clearTimeout(timer)
  }, [index])

  const step = CYCLE[index]
  return (
    <div role="status" className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">Following your request through the system…</p>
      <div className="flex items-stretch" aria-hidden="true">
        {NODES.map((node, i) => (
          <Fragment key={node.label}>
            <NodeCard node={node} active={step.kind === "stay" && step.node === i} />
            {i < NODES.length - 1 && (
              <Lane hop={step.kind === "hop" && step.lane === i ? step.direction : null} stepKey={index} />
            )}
          </Fragment>
        ))}
      </div>
    </div>
  )
}

function NodeCard({ node, active }: { node: FlowNode; active: boolean }) {
  const Icon = node.icon
  return (
    <Card
      size="sm"
      className={cn(
        "relative z-10 min-w-0 flex-1 items-center justify-center gap-1.5 px-0.5 py-3 text-center transition-[box-shadow,translate] duration-300 sm:w-24 sm:flex-none sm:gap-2 sm:py-4",
        active && "-translate-y-0.5 shadow-lg ring-foreground/40",
      )}
    >
      <span
        className={cn(
          "flex size-8 items-center justify-center rounded-lg bg-muted text-muted-foreground transition-colors duration-300 sm:size-10",
          active && "bg-primary text-primary-foreground",
        )}
      >
        <Icon className="size-4 sm:size-5" />
      </span>
      <span className="text-[9px] leading-tight font-medium sm:text-xs">{node.label}</span>
      {node.detail && <span className="hidden text-[11px] leading-none text-muted-foreground sm:block">{node.detail}</span>}
    </Card>
  )
}

function Lane({ hop, stepKey }: { hop: Direction | null; stepKey: number }) {
  return (
    <div className="relative w-3 shrink-0 sm:w-auto sm:flex-1">
      <Track direction="out" active={hop === "out"} />
      <Track direction="back" active={hop === "back"} />
      {hop && (
        <span
          // A new key restarts the CSS animation on every hop
          key={stepKey}
          style={{ animationDuration: `${HOP_MS}ms` }}
          className={cn(
            "absolute flex size-6 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-md motion-reduce:hidden sm:size-7",
            hop === "out" ? "top-[38%] animate-packet-out" : "top-[62%] animate-packet-back",
          )}
        >
          <Package className="size-3.5" />
        </span>
      )}
    </div>
  )
}

function Track({ direction, active }: { direction: Direction; active: boolean }) {
  const Arrow = direction === "out" ? ChevronRight : ChevronLeft
  return (
    <div
      className={cn(
        "absolute inset-x-0.5 h-px -translate-y-1/2 bg-border transition-colors duration-300",
        direction === "out" ? "top-[38%]" : "top-[62%]",
        active && "bg-foreground/50",
      )}
    >
      <Arrow
        className={cn(
          "absolute top-1/2 size-3.5 -translate-y-1/2 text-border transition-colors duration-300",
          direction === "out" ? "-right-1.5" : "-left-1.5",
          active && "text-foreground/50",
        )}
      />
    </div>
  )
}
