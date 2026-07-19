export async function runTraceRequest<T>(input: Readonly<{
  execute: () => Promise<T>;
  onRejected: () => void;
  onSettled: () => void;
}>): Promise<T | null> {
  try {
    return await input.execute();
  } catch {
    input.onRejected();
    return null;
  } finally {
    input.onSettled();
  }
}
