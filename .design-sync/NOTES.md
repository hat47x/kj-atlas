design-sync configuration for kj-atlas

This directory holds this repository's own configuration and overrides for
an external tool called design-sync, which converts kj-atlas's frontend
component set into a bundle uploadable to Claude Design. The tool itself
(its build/validate scripts, its own node_modules) is not part of this
repository -- it is installed separately, wherever it is run from, and is
invoked with this repository's frontend package as its target and this
directory's config.json as its configuration.

config.json

Points the tool at the frontend package (03_Implement/frontend), the global
name the bundle exposes on window, and componentSrcMap: { "App": null },
which excludes the top-level App shell from the synced component list (it is
the whole-application composition, not a reusable piece).

overrides/source-kit.mjs

A declared, repo-local fork of the tool's own "package" source-discovery
adapter (declared via config.json's libOverrides key, which the tool
requires -- an undeclared fork fails the build loudly). It makes one
behavioral change: it excludes 03_Implement/frontend/src/main.tsx from the
bundle's module sweep.

Why: main.tsx calls ReactDOM.createRoot(document.getElementById("root")!) at
module scope -- a plain assumption that the page it runs in has a #root
element, true for the real app's index.html. The tool's own render-check
validator loads the built bundle in a page with no such element present, so
that assertion throws the moment the bundle is evaluated, aborting the
bundle's module initialization before any component is exposed on window.
Every one of the frontend's 50 components then reports as "not exported" --
a single unrelated app-bootstrap file, not an actual export problem.

componentSrcMap can't reach this: it only pins or excludes names in the
already-discovered component list, and main.tsx exports no component name at
all, so it never appears there to be excluded. The exclusion has to happen
at the file-sweep stage, which is exactly what the source-kit adapter is
responsible for -- hence the fork.

The fork also reimplements the tool's fallback component-name derivation
(used because this package ships no built dist/.d.ts) with a plain regular-
expression scan instead of the original's AST-based one, because the fork
lives outside the tool's own installed directory and can no longer reach the
AST library it depends on. This was verified to produce the identical
50-component set as the original derivation for this repository's current
source tree before being adopted.

Reproducing a build

From wherever the design-sync tool is installed, with this repository's
03_Implement/frontend mirrored or checked out alongside it: run the tool's
own package-build step pointed at this directory's config.json, then its
package-validate step against the output directory. The validator should
report all 50 components present with no BUNDLE_EXPORT failures. A small
number of non-blocking render-check warnings are expected and already
understood: two components (the app shell and a diff-preview panel) render
as an intentional typographic placeholder because they have no authored
preview yet, and are not implementation defects.
