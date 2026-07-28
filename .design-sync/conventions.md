kj-atlas is a package-shape design system with no built dist/ — every sync
synthesizes its bundle entry directly from src/. componentSrcMap excludes
the top-level App component (the whole-app composition, not a reusable
piece); overrides/source-kit.mjs additionally excludes src/main.tsx, whose
module-scope ReactDOM.createRoot(getElementById("root")!) would otherwise
throw during headless bundle evaluation (see the repo's
.design-sync/NOTES.md for the full root cause).

Most components here are canvas/workspace panels that expect real document
state, active-selection context, or a live provider tree to render
meaningfully outside the running app. Rather than hand-author preview
fixtures for all of them up front, this first sync accepts the generated
typographic floor card for components without an authored preview under
.design-sync/previews/ — that is a deliberate, reviewed placeholder, not a
missed conversion. Two components (the app shell and a diff-preview panel)
are the only ones without authored previews with a render worth noting: they
render blank rather than a floor card because they mount successfully but
paint nothing meaningful with no props supplied.

Authoring real previews under .design-sync/previews/<Name>.tsx for the
highest-value components is expected future work, not a blocker for this
sync.
