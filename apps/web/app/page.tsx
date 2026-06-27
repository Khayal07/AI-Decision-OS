import { DecisionExperience } from "@/components/decision/decision-experience";

export default function Home() {
  return (
    <main className="relative isolate min-h-screen overflow-hidden">
      {/* Ambient gradient */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 -top-40 -z-10 flex justify-center"
      >
        <div className="h-[36rem] w-[36rem] rounded-full bg-accent/20 blur-[140px]" />
      </div>

      <div className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center px-6 py-20 text-center">
        <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-muted/40 px-3 py-1 text-xs text-muted-foreground">
          <span className="h-1.5 w-1.5 rounded-full bg-accent" />
          AI Decision OS
        </span>

        <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-6xl">
          Make any decision with
          <span className="bg-gradient-to-r from-accent to-foreground bg-clip-text text-transparent">
            {" "}
            confidence
          </span>
          .
        </h1>

        <p className="mt-5 max-w-xl text-pretty text-base text-muted-foreground sm:text-lg">
          Describe your decision in one sentence. Our multi-agent AI researches, scores, and
          stress-tests every option — then hands you a clear, visual recommendation in under 30
          seconds.
        </p>

        <div className="mt-10 w-full max-w-xl">
          <DecisionExperience />
        </div>

        <p className="mt-16 text-xs text-muted-foreground">
          Reasoned · Personalized · Explainable
        </p>
      </div>
    </main>
  );
}
