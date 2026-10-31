import { BookOpenText, SquarePen } from "lucide-react"

import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"

interface AppHeaderProps {
  canReset: boolean
  onReset: () => void
}

export function AppHeader({ canReset, onReset }: AppHeaderProps) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between px-3 sm:px-4">
      <div className="flex items-center gap-2.5 px-1">
        <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <BookOpenText className="size-4.5" aria-hidden="true" />
        </span>
        <span className="text-lg font-semibold tracking-tight">SmartWiki</span>
      </div>
      <div className="flex items-center gap-1">
        <ThemeToggle />
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" onClick={onReset} disabled={!canReset} aria-label="New chat">
              <SquarePen />
            </Button>
          </TooltipTrigger>
          <TooltipContent>New chat</TooltipContent>
        </Tooltip>
      </div>
    </header>
  )
}
