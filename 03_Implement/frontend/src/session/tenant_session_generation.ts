export class StaleTenantSessionResultError extends Error {
  constructor() {
    super("Tenant-scoped result belongs to an invalidated session generation");
    this.name = "StaleTenantSessionResultError";
  }
}

/**
 * Prevents a successful async result from being committed after the App's
 * tenant-bound runtime resources have been invalidated.
 */
export class TenantSessionGenerationGuard {
  private generation = 0;

  invalidate(): void {
    this.generation += 1;
  }

  async run<T>(request: () => Promise<T>): Promise<T> {
    const requestGeneration = this.generation;
    const result = await request();
    if (requestGeneration !== this.generation) {
      throw new StaleTenantSessionResultError();
    }
    return result;
  }
}
