export type ComputeProgress = {
  message: string;
  completed: number;
  total: number;
};

export type ComputeTaskContext = {
  isCancelled: () => boolean;
  reportProgress: (progress: ComputeProgress) => void;
  yieldToMainThread: () => Promise<void>;
};

export type RunTaskResult<T> =
  | { status: "completed"; result: T }
  | { status: "cancelled" };

export async function yieldToMainThread(): Promise<void> {
  if (typeof window !== "undefined" && typeof window.requestIdleCallback === "function") {
    await new Promise<void>((resolve) => {
      window.requestIdleCallback(() => resolve());
    });
    return;
  }

  await new Promise<void>((resolve) => {
    setTimeout(resolve, 0);
  });
}

export function createCancelableTaskRunner() {
  let cancelled = false;
  const progressListeners = new Set<(progress: ComputeProgress) => void>();

  return {
    async run<T>(task: (ctx: ComputeTaskContext) => Promise<T>): Promise<RunTaskResult<T>> {
      cancelled = false;
      const ctx: ComputeTaskContext = {
        isCancelled: () => cancelled,
        reportProgress: (progress) => {
          for (const listener of progressListeners) {
            listener(progress);
          }
        },
        yieldToMainThread,
      };

      const result = await task(ctx);
      if (cancelled) {
        return { status: "cancelled" };
      }

      return { status: "completed", result };
    },
    cancel() {
      cancelled = true;
    },
    onProgress(listener: (progress: ComputeProgress) => void) {
      progressListeners.add(listener);
      return () => {
        progressListeners.delete(listener);
      };
    },
  };
}
