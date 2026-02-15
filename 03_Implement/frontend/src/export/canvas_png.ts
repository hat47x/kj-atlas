export type PngExportScale = 1 | 2;

type ExportSvgToPngBlobInput = {
  svg: string;
  width: number;
  height: number;
  scale?: PngExportScale;
};

function loadImageFromObjectUrl(objectUrl: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      resolve(image);
    };
    image.onerror = () => {
      reject(new Error("Failed to load SVG image for PNG export"));
    };
    image.src = objectUrl;
  });
}

function canvasToPngBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error("Failed to encode PNG blob"));
        return;
      }
      resolve(blob);
    }, "image/png");
  });
}

export async function exportSvgToPngBlob({ svg, width, height, scale = 1 }: ExportSvgToPngBlobInput): Promise<Blob> {
  if (width <= 0 || height <= 0) {
    throw new Error("Invalid export dimensions");
  }

  const svgBlob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
  const objectUrl = URL.createObjectURL(svgBlob);

  try {
    const image = await loadImageFromObjectUrl(objectUrl);
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.ceil(width * scale));
    canvas.height = Math.max(1, Math.ceil(height * scale));

    const context = canvas.getContext("2d");
    if (!context) {
      throw new Error("Canvas 2D context is unavailable");
    }

    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    return await canvasToPngBlob(canvas);
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

export function downloadBlobFile(filename: string, blob: Blob): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

