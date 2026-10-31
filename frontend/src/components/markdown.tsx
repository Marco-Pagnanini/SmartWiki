import ReactMarkdown, { type Components } from "react-markdown"

// The agents answer in Markdown: map each element to the chat's typography
const components: Components = {
  p: (props) => <p className="my-3 first:mt-0 last:mb-0" {...props} />,
  ul: (props) => <ul className="my-3 list-disc space-y-1 pl-6" {...props} />,
  ol: (props) => <ol className="my-3 list-decimal space-y-1 pl-6" {...props} />,
  strong: (props) => <strong className="font-semibold" {...props} />,
  a: (props) => <a className="font-medium underline underline-offset-4" target="_blank" rel="noreferrer" {...props} />,
  code: (props) => <code className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-[0.875em]" {...props} />,
  h1: (props) => <h3 className="mt-5 mb-2 text-lg font-semibold" {...props} />,
  h2: (props) => <h3 className="mt-5 mb-2 text-base font-semibold" {...props} />,
  h3: (props) => <h3 className="mt-4 mb-2 text-base font-semibold" {...props} />,
}

export function Markdown({ children }: { children: string }) {
  return <ReactMarkdown components={components}>{children}</ReactMarkdown>
}
