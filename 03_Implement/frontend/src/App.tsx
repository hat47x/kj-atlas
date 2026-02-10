import { CanvasShell } from "./canvas/CanvasShell";
import { Shell } from "./ui/Shell";

export default function App() {
  return (
    <Shell title="kj-atlas Canvas MVP">
      <CanvasShell />
    </Shell>
  );
}
