# ADR-0029: Third-party runtime environment boundary

- Status: Accepted
- Date: 2026-05-10
- Deciders: Project Maintainers
- Scope: `03_Implement/deploy/`, `02_Architecture/runtime_parameter_registry.md`, `04_Documentation/configuration.md`

## Context

ADR-0021 accepts `KJ_ATLAS_*` as the only supported namespace for kj-atlas runtime environment variables.

The Compose deployment still uses third-party components, especially the official PostgreSQL container image. That image has its own container environment contract. The project therefore needs an explicit decision boundary for the difference between:

- public variables that users and operators configure for kj-atlas; and
- private adapter variables required by third-party images or build tools.

Without this boundary, the statement "all environment variables must start with `KJ_ATLAS_`" can be interpreted in two incompatible ways:

1. all public kj-atlas settings must use `KJ_ATLAS_*`; or
2. no process in the deployment may ever receive any other environment-variable name, including vendor-defined names.

The current implementation satisfies the first interpretation. It does not satisfy the second because the PostgreSQL image consumes vendor-defined names inside the `db` service boundary.

## Decision

All project-owned and user-facing runtime environment variables MUST start with `KJ_ATLAS_`.

Non-`KJ_ATLAS_*` variables MUST NOT be documented, accepted, or required as public kj-atlas settings.

If a third-party image or build tool requires a vendor-defined environment name, kj-atlas may map from `KJ_ATLAS_*` inputs to that private name at the service or build boundary. This mapping is an adapter boundary, not a public configuration exception.

Direct user configuration of vendor-defined names is not supported. Public documentation and runbooks must instruct users to set only `KJ_ATLAS_*` variables.

If maintainers require the stricter interpretation that no process environment in any bundled deployment may contain a non-`KJ_ATLAS_*` name, treat that as a separate architecture change. In that case, the PostgreSQL service must be replaced with a project-owned initialization/runtime path or with a managed-database-only deployment before the issue can be marked Done.

Non-goals:

- Redesign the database topology in this ADR.
- Add compatibility support for legacy unprefixed project variables.
- Change SafeMode, access-control, or export behavior.


## Boundary contract matrix

| Boundary | Key namespace | Who sets it | Where it appears | Rule |
| --- | --- | --- | --- | --- |
| Public runtime contract | `KJ_ATLAS_*` only | Users / operators | Runtime registry, configuration docs, Compose input surface | MUST be documented and supported as public keys. |
| Private adapter boundary | vendor-defined names (for example `POSTGRES_*`) | Compose/build implementation only | Third-party container `environment` / build internals | MUST NOT be exposed as public configuration keys. |

## Consequences

Expected benefits:

- Keeps the public configuration contract simple and auditable.
- Lets kj-atlas continue to use standard third-party images without exposing their environment APIs to users.
- Gives documentation a precise rule: users set only `KJ_ATLAS_*`; implementation adapters may translate internally.

Constraints and risks:

- Source files may still contain vendor-defined names where a third-party adapter requires them.
- Automated checks must distinguish public configuration keys from private adapter keys.
- A future "no non-prefixed process environment anywhere" requirement is a deployment redesign, not a documentation cleanup.


## C/D/C log (for ENV-CONFIG-DRIFT-01)

### Confirmed

- Public runtime contract uses `KJ_ATLAS_*` keys only.
- Vendor/build-tool specific names are allowed only inside adapter boundaries (Compose service internals, build-time bridge variables).
- Public docs and runtime registry must never ask operators to set vendor-defined names directly.

### Decided

- Keep adapter-boundary interpretation as the accepted operating model for Compose + third-party images in this phase.
- Treat vendor-defined process env names inside third-party containers as implementation details, not public contract exceptions.

### Clarified pending

- If project policy later upgrades to "no non-`KJ_ATLAS_*` process env names anywhere", that requires deployment redesign (replace PostgreSQL image path or enforce managed DB-only architecture).
- `external_http` adapter behavior when endpoint is absent remains a separate governance decision and is not changed by this ADR.

## Traceability

- Related: `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`
- Related: `02_Architecture/runtime_parameter_registry.md`
- Related: `03_Implement/deploy/docker-compose.yml`
- Related issue: `01_Plans/issues/issue-ENV-CONFIG-DRIFT-01-runtime-configuration-contract-alignment.md`
- Derived-from: `01_Plans/adr/ADR-0001-value-to-requirements.md`


## Public key set (frozen for ENV-CONFIG-DRIFT-01)

The public runtime key set is frozen to keys listed in `02_Architecture/runtime_parameter_registry.md` and all of them MUST use `KJ_ATLAS_*`.

Any future requirement to ban all vendor-defined process environment names (including third-party container internals) is **not** an interpretation tweak of this ADR; it is a separate design-change track that requires a replacement deployment architecture.
