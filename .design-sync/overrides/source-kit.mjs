// Non-storybook `package` adapter. Bundles dist/ when present (the authoritative
// component list comes from shipped .d.ts; with no dist it synthesizes an
// entry from src/ as a last resort) and opportunistically enriches each
// component from src/ — JSDoc and dir-derived group. Every enrichment miss
// degrades to the plain-dist behaviour.
//
// Discovery is heuristic-based; each heuristic has a `.design-sync/config.json`
// override (ASSUMPTION comments below name them) so repos that don't match the
// defaults write config, not code. `componentSrcMap` is the single override
// knob for component inclusion: non-null value = add/pin src path, null =
// exclude a .d.ts-exported internal.
//
// FORK (kj-atlas, declared in cfg.libOverrides["source-kit.mjs"]):
//
// 1) EXCLUDE_APP_ENTRY — the upstream synth-entry sweep has no way to
// exclude a non-component file from the bundle's module graph. src/main.tsx
// calls ReactDOM.createRoot(document.getElementById("root")!) at module
// scope. design-sync's own render-check validator loads the bundle with no
// #root element present, so that assertion throws synchronously while the
// bundle evaluates — aborting the whole IIFE before window.<GlobalName> is
// ever assigned. Every component then reads as "not exported"
// ([BUNDLE_EXPORT] 50/50), a cascading false negative from one unrelated
// app-bootstrap file, not a real export problem. cfg.componentSrcMap can't
// reach this: main.tsx exports zero PascalCase components, so it never
// enters the name-keyed component list componentSrcMap operates on — the
// exclusion has to happen at the file-sweep level, which only this adapter
// controls. Marked APP_ENTRY_RX below.
//
// 2) NO_TS_MORPH — this fork is a physically separate file living under
// .design-sync/overrides/ (a repo-committed directory), not under the
// design-sync tool's own .ds-sync/lib/. Node's ESM resolver walks ANCESTOR
// directories for bare specifiers (e.g. `import ... from 'ts-morph'`);
// .ds-sync/node_modules is a SIBLING of .design-sync/, not an ancestor, so
// the upstream file's `import { Project, Node, ts } from 'ts-morph'` cannot
// resolve from here (confirmed: ERR_MODULE_NOT_FOUND). deriveComponentsFromSrc
// below is reimplemented with a plain regex scan instead of a ts-morph AST
// walk — the same lighter-weight technique this file already uses a few
// lines down for src-file enrichment (see `exportRx` in the per-component
// loop). Empirically verified equivalent for this repo: diffed the full
// 50-component output against the original ts-morph-based derivation
// (2026-07-28) — identical set. If a future component's export syntax isn't
// PascalCase `export const|let|var|function|class Name` or
// `export default function|class Name`, it could be missed; the build's own
// printed component count and the design-sync render-check/CI gate would
// surface any such regression immediately (a silent drop, not a crash).
//
// The three relative imports below (common.mjs/bundle.mjs/dts.mjs) point
// directly at the tool's own stable lib files via an explicit `../../`
// relative path, not a bare specifier — this is a plain file-path import
// (no ancestor-walk involved) and carries no third-party-dependency risk.
// It assumes `.ds-sync/` sits as a sibling of `.design-sync/` at the same
// root, which is already the tool's own documented CWD-relative invocation
// convention (BUNDLED_LIB/REPO_LIB in package-build.mjs are anchored the
// same way) — not a new assumption introduced by this fork.

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { leadingJsdoc, readText, slash, walk } from '../../.ds-sync/lib/common.mjs';
import { resolveDistEntry } from '../../.ds-sync/lib/bundle.mjs';
import { exportedNames, isComponentName } from '../../.ds-sync/lib/dts.mjs';

const NON_IMPL_RX = /\.(stories|test|spec)\./;
const SRC_IMPL_RX = /\.(tsx|jsx)$/;
// FORK: app-bootstrap entry points excluded from the synth-entry sweep (see
// FORK note 1 above). Extend this list, don't remove the mechanism, if
// another module-scope-side-effect file needs the same treatment.
const APP_ENTRY_RX = /\/src\/main\.tsx$/;
// FORK: regex-based named-export scan, replacing the ts-morph AST walk (see
// FORK note 2 above). Mirrors ts-morph's own filter: only const/let/var/
// function/class declarations count (excludes `export type`/`export
// interface`), and a default export must be a *named* function/class
// declaration to be recoverable (an anonymous `export default () => {}` is
// skipped, matching the original's `decls.map(d => d.getName?.())` miss).
const NAMED_EXPORT_RX = /^export\s+(?:const|let|var|function\*?|class)\s+([A-Z][A-Za-z0-9]*)\b/gm;
const DEFAULT_NAMED_EXPORT_RX = /^export\s+default\s+(?:function\*?|class)\s+([A-Z][A-Za-z0-9]*)\b/gm;
// Dir names that don't usefully group components — skip so the emitted path
// is `components/<group>/<Name>` not `components/components/<Name>`.
const GENERIC_DIR = new Set(['components', 'component', 'src', 'lib', 'ui', 'packages', 'react']);
const slug = (s) => s.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'general';

// No .d.ts → scan src files for PascalCase value exports via regex (FORK note 2).
function deriveComponentsFromSrc(srcFiles) {
  const seen = new Set();
  for (const p of srcFiles) {
    if (NON_IMPL_RX.test(p) || !SRC_IMPL_RX.test(p)) continue;
    const text = readFileSync(p, 'utf8');
    for (const rx of [NAMED_EXPORT_RX, DEFAULT_NAMED_EXPORT_RX]) {
      rx.lastIndex = 0;
      let m;
      while ((m = rx.exec(text))) seen.add(m[1]);
    }
  }
  return [...seen].sort().map((name) => ({ name, group: 'general' }));
}

export async function resolvePackage(ctx) {
  const { PKG_DIR, pkgJson, ENTRY_OVERRIDE, PKG, OUT, cfg } = ctx;
  const srcMap = cfg.componentSrcMap ?? {};

  // ── 1. src/ discovery (best-effort; feeds enrichment + synth-entry fallback).
  // ASSUMPTION: source root is first of src/ | lib/ | components/. Override: cfg.srcDir.
  const srcRoot = [cfg.srcDir, 'src', 'lib', 'components']
    .map((d) => d && resolve(PKG_DIR, d))
    .find((d) => d && existsSync(d));
  const srcFiles = srcRoot ? walk(srcRoot, (n) => /\.(tsx|jsx|mdx?)$/.test(n)) : [];

  // ── 2. entry: dist if it exists, else synthesize from src/ (last resort).
  let entry = resolveDistEntry({ pkgDir: PKG_DIR, pkgJson, override: ENTRY_OVERRIDE, pkgName: PKG, soft: true });
  let synthEntry = false;
  if (!entry) {
    if (!srcRoot) {
      console.error(`[NO_DIST] ${PKG} has no built entry and no src/ to synthesize from — run its build.`);
      process.exit(1);
    }
    // FORK: `&& !APP_ENTRY_RX.test(p)` — see FORK note 1 at the top of this file.
    const comps = srcFiles.filter((p) => SRC_IMPL_RX.test(p) && !NON_IMPL_RX.test(p) && !APP_ENTRY_RX.test(p));
    entry = join(OUT, '.pkg-entry.mjs');
    writeFileSync(entry, comps.map((p) => `export * from ${JSON.stringify(p)};`).join('\n') + '\n');
    synthEntry = true;
    console.error(
      `[NO_DIST] no built entry — synthesizing from ${comps.length} src files (run the package's build for best results)`,
    );
  }

  // ── 3. component list: from shipped .d.ts (authoritative when dist exists).
  // ASSUMPTION: components = PascalCase value exports in the .d.ts tree.
  // Override: cfg.componentSrcMap (non-null adds/pins, null excludes).
  const exported = exportedNames(PKG_DIR, pkgJson);
  const names = new Set([...exported].filter(isComponentName));
  for (const [k, v] of Object.entries(srcMap)) {
    if (v === null) { names.delete(k); continue; }
    // Names reach `<script>` blocks in the emitted HTML — reject anything
    // that isn't a plain PascalCase identifier.
    if (!/^[A-Z][A-Za-z0-9]*$/.test(k)) {
      console.error(`[CONFIG] componentSrcMap: "${k}" is not a valid component name (PascalCase identifiers only)`);
      continue;
    }
    names.add(k);
  }
  let components = [...names].sort().map((name) => ({ name, group: 'general' }));
  if (!components.length && synthEntry) {
    components = deriveComponentsFromSrc(srcFiles).filter((c) => srcMap[c.name] !== null);
  }
  if (!components.length) {
    if (cfg.cssEntry || existsSync(join(PKG_DIR, 'styles.css'))) {
      console.error('[ZERO_MATCH] no component exports — treating as tokens-only DS');
      return { shape: 'package', entry, components: [], tokensOnly: true };
    }
    console.error(`[ZERO_MATCH] no PascalCase exports in ${PKG} and no styles — nothing to sync`);
    process.exit(1);
  }

  // ── 4. src/ enrichment per component. Every miss degrades to plain-dist.
  if (srcRoot) {
    for (const c of components) {
      // Pinned via config → skip fuzzy-find entirely.
      let hit = typeof srcMap[c.name] === 'string' ? slash(resolve(PKG_DIR, srcMap[c.name])) : null;
      if (!hit) {
        // ASSUMPTION: <Name>.tsx | <name>/<name>.tsx | <Name>/index.tsx |
        // <kebab-name>.tsx, case-insensitive; dir-match ranks above
        // bare-file match, then prefer one that actually exports `c.name`.
        // Override: cfg.componentSrcMap.
        const kebab = c.name.replace(/([a-z0-9])([A-Z])/g, '$1-$2');
        const nameRx = new RegExp(
          `(?:^|/)(?:${c.name}/(?:index|${c.name})\\.(tsx|jsx)|(?:${c.name}|${kebab})\\.(tsx|jsx))$`,
          'i',
        );
        const hits = srcFiles
          .filter((p) => nameRx.test(p) && !NON_IMPL_RX.test(p))
          .sort(
            (a, b) =>
              (b.toLowerCase().includes(`/${c.name.toLowerCase()}/`) ? 1 : 0) -
              (a.toLowerCase().includes(`/${c.name.toLowerCase()}/`) ? 1 : 0),
          );
        const exportRx = new RegExp(`export\\s+(?:default\\s+)?(?:const|let|var|function|class)\\s+${c.name}\\b`);
        hit = hits.find((p) => exportRx.test(readText(p))) ?? hits[0];
      }
      if (!hit || !existsSync(hit)) continue;
      c.srcPath = hit;
      c.doc = leadingJsdoc(readText(hit), c.name) || undefined;
      // group = last src/ path segment that isn't the component's own dir or
      // a generic container name — else JSDoc @category — else 'general'.
      c.group = slug(
        slash(relative(srcRoot, dirname(hit)))
          .split('/')
          .filter((s) => s && s.toLowerCase() !== c.name.toLowerCase() && !GENERIC_DIR.has(s.toLowerCase()))
          .at(-1)
        || (c.doc && /@category\s+(\S+)/.exec(c.doc)?.[1])
        || 'general',
      );
    }
  }

  console.error(
    `  package: ${components.length} components` +
      (srcRoot ? ` (${components.filter((c) => c.srcPath).length} src-matched)` : ' (no src/ — dist-only)'),
  );
  return { shape: 'package', entry, components, synthEntry, exported };
}
