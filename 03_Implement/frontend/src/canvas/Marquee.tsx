type MarqueeProps = {
  rect: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
};

export function Marquee({ rect }: MarqueeProps) {
  return (
    <div
      aria-hidden="true"
      style={{
        position: "absolute",
        left: rect.x,
        top: rect.y,
        width: rect.width,
        height: rect.height,
        border: "1px solid #2563eb",
        backgroundColor: "rgba(37, 99, 235, 0.16)",
        pointerEvents: "none",
      }}
    />
  );
}
