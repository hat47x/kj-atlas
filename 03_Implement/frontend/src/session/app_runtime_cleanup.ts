type Abortable = Readonly<{ abort: () => void }>;
type Cancelable = Readonly<{ cancel: () => void }>;
type Disposable = Readonly<{ dispose: () => void }>;

export type AppRuntimeCleanupResult = Readonly<{
  attemptedSteps: number;
  failureCount: number;
}>;

function runCleanupSteps(steps: readonly (() => void)[]): AppRuntimeCleanupResult {
  let failureCount = 0;
  for (const step of steps) {
    try {
      step();
    } catch {
      failureCount += 1;
    }
  }
  return {
    attemptedSteps: steps.length,
    failureCount,
  };
}

export function cleanupAppRuntimeResources(input: Readonly<{
  abortControllers: readonly (Abortable | null | undefined)[];
  cancelableTasks: readonly (Cancelable | null | undefined)[];
  disposableWorkers: readonly (Disposable | null | undefined)[];
}>): AppRuntimeCleanupResult {
  return runCleanupSteps([
    ...input.abortControllers
      .filter((controller): controller is Abortable => Boolean(controller))
      .map((controller) => () => controller.abort()),
    ...input.cancelableTasks
      .filter((task): task is Cancelable => Boolean(task))
      .map((task) => () => task.cancel()),
    ...input.disposableWorkers
      .filter((worker): worker is Disposable => Boolean(worker))
      .map((worker) => () => worker.dispose()),
  ]);
}
