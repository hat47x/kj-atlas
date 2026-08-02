import { useEffect, useRef, useState, type ChangeEvent } from "react";

import {
  deleteRepresentativeVisualCueAsset,
  saveUserImageCueAsset,
  USER_IMAGE_CUE_ASSET_MAX_BYTES,
  USER_IMAGE_CUE_DIMENSION,
} from "../domain/representative_visual_cue_assets";
import type { RepresentativeVisualCue } from "../domain/types";
import { t } from "../i18n/translate";
import { useRepresentativeVisualCueAssetScope } from "./RepresentativeVisualCueAssetScope";

const SOURCE_IMAGE_MAX_BYTES = 10 * 1024 * 1024;
const SOURCE_IMAGE_MAX_DIMENSION = 8000;
const ACCEPTED_SOURCE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

type Props = {
  documentId: string;
  disabled: boolean;
  onAdopt: (cue: RepresentativeVisualCue) => boolean;
};

type LoadedSource = {
  image: HTMLImageElement;
  objectUrl: string;
};

function canvasToPng(canvas: HTMLCanvasElement): Promise<Uint8Array> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error("failed to encode image crop"));
        return;
      }
      void blob.arrayBuffer()
        .then((buffer) => resolve(new Uint8Array(buffer)))
        .catch(reject);
    }, "image/png");
  });
}

export function RepresentativeVisualCueImageEditor({ documentId, disabled, onAdopt }: Props) {
  const scope = useRepresentativeVisualCueAssetScope();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const previewRef = useRef<HTMLCanvasElement | null>(null);
  const pendingObjectUrlRef = useRef<string | null>(null);
  const [source, setSource] = useState<LoadedSource | null>(null);
  const [cropX, setCropX] = useState(50);
  const [cropY, setCropY] = useState(50);
  const [zoom, setZoom] = useState(1);
  const [isSaving, setIsSaving] = useState(false);
  const [isPreviewReady, setIsPreviewReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => () => {
    if (pendingObjectUrlRef.current) {
      URL.revokeObjectURL(pendingObjectUrlRef.current);
    }
  }, []);

  useEffect(() => () => {
    if (source) {
      URL.revokeObjectURL(source.objectUrl);
    }
  }, [source]);

  useEffect(() => {
    const canvas = previewRef.current;
    if (!canvas || !source) {
      setIsPreviewReady(false);
      return;
    }
    setIsPreviewReady(false);
    const context = canvas.getContext("2d");
    if (!context) {
      setError(t("side_panel.visual_cue.user_image.decode_error"));
      return;
    }
    const { naturalWidth: width, naturalHeight: height } = source.image;
    const cropSide = Math.min(width, height) / zoom;
    const sourceX = ((width - cropSide) * cropX) / 100;
    const sourceY = ((height - cropSide) * cropY) / 100;
    context.clearRect(0, 0, USER_IMAGE_CUE_DIMENSION, USER_IMAGE_CUE_DIMENSION);
    context.save();
    context.filter = "grayscale(35%) saturate(70%)";
    context.drawImage(
      source.image,
      sourceX,
      sourceY,
      cropSide,
      cropSide,
      0,
      0,
      USER_IMAGE_CUE_DIMENSION,
      USER_IMAGE_CUE_DIMENSION,
    );
    context.restore();
    setIsPreviewReady(true);
  }, [cropX, cropY, source, zoom]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || disabled || isSaving) {
      return;
    }
    setError(null);
    if (!ACCEPTED_SOURCE_TYPES.has(file.type) || file.size === 0 || file.size > SOURCE_IMAGE_MAX_BYTES) {
      setError(t("side_panel.visual_cue.user_image.file_error"));
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    if (pendingObjectUrlRef.current) {
      URL.revokeObjectURL(pendingObjectUrlRef.current);
    }
    pendingObjectUrlRef.current = objectUrl;
    const image = new Image();
    image.decoding = "async";
    image.onload = () => {
      if (pendingObjectUrlRef.current !== objectUrl) {
        return;
      }
      if (
        image.naturalWidth === 0
        || image.naturalHeight === 0
        || image.naturalWidth > SOURCE_IMAGE_MAX_DIMENSION
        || image.naturalHeight > SOURCE_IMAGE_MAX_DIMENSION
      ) {
        pendingObjectUrlRef.current = null;
        URL.revokeObjectURL(objectUrl);
        setError(t("side_panel.visual_cue.user_image.dimension_error"));
        return;
      }
      pendingObjectUrlRef.current = null;
      setSource({ image, objectUrl });
      setCropX(50);
      setCropY(50);
      setZoom(1);
    };
    image.onerror = () => {
      if (pendingObjectUrlRef.current !== objectUrl) {
        return;
      }
      pendingObjectUrlRef.current = null;
      URL.revokeObjectURL(objectUrl);
      setError(t("side_panel.visual_cue.user_image.decode_error"));
    };
    image.src = objectUrl;
  };

  const handleAdopt = async () => {
    const canvas = previewRef.current;
    if (!canvas || !source || !isPreviewReady || disabled || isSaving) {
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const pngBytes = await canvasToPng(canvas);
      if (pngBytes.byteLength > USER_IMAGE_CUE_ASSET_MAX_BYTES) {
        throw new Error("cropped user image exceeds storage limit");
      }
      const imageRef = await saveUserImageCueAsset(documentId, pngBytes, scope);
      const adopted = onAdopt({
        kind: "user_image",
        cueId: imageRef,
        imageRef,
        altText: t("side_panel.visual_cue.user_image.default_alt"),
      });
      if (!adopted) {
        await deleteRepresentativeVisualCueAsset(imageRef, scope);
        throw new Error("document rejected the visual cue");
      }
      setSource(null);
    } catch {
      setError(t("side_panel.visual_cue.user_image.save_error"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      data-visual-cue-editor="user-image"
      style={{ display: "grid", gap: 8, borderTop: "1px solid #e2e8f0", paddingTop: 8 }}
    >
      <div style={{ fontSize: 12, fontWeight: 700, color: "#334155" }}>
        {t("side_panel.visual_cue.user_image.title")}
      </div>
      <div style={{ fontSize: 11, lineHeight: 1.5, color: "#475569" }}>
        {t("side_panel.visual_cue.user_image.instructions")}
      </div>
      <button
        type="button"
        disabled={disabled || isSaving}
        onClick={() => inputRef.current?.click()}
      >
        {t("side_panel.visual_cue.user_image.choose")}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        disabled={disabled || isSaving}
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
      {source ? (
        <>
          <canvas
            ref={previewRef}
            role="img"
            aria-label={t("side_panel.visual_cue.user_image.preview")}
            width={USER_IMAGE_CUE_DIMENSION}
            height={USER_IMAGE_CUE_DIMENSION}
            style={{
              width: 120,
              height: 120,
              maxWidth: "100%",
              justifySelf: "center",
              border: "1px solid #94a3b8",
              borderRadius: 6,
              backgroundColor: "#ffffff",
            }}
          />
          <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#475569" }}>
            {t("side_panel.visual_cue.user_image.horizontal")}
            <input
              type="range"
              min={0}
              max={100}
              value={cropX}
              disabled={disabled || isSaving}
              onChange={(event) => setCropX(Number(event.target.value))}
            />
          </label>
          <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#475569" }}>
            {t("side_panel.visual_cue.user_image.vertical")}
            <input
              type="range"
              min={0}
              max={100}
              value={cropY}
              disabled={disabled || isSaving}
              onChange={(event) => setCropY(Number(event.target.value))}
            />
          </label>
          <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#475569" }}>
            {t("side_panel.visual_cue.user_image.zoom")}
            <input
              type="range"
              min={1}
              max={3}
              step={0.1}
              value={zoom}
              disabled={disabled || isSaving}
              onChange={(event) => setZoom(Number(event.target.value))}
            />
          </label>
          <button
            type="button"
            disabled={disabled || isSaving || !isPreviewReady}
            onClick={() => void handleAdopt()}
          >
            {isSaving
              ? t("side_panel.visual_cue.user_image.saving")
              : t("side_panel.visual_cue.user_image.adopt")}
          </button>
        </>
      ) : null}
      <div role="status" style={{ minHeight: 18, fontSize: 11, color: error ? "#b91c1c" : "#475569" }}>
        {error ?? t("side_panel.visual_cue.user_image.local_only")}
      </div>
    </div>
  );
}
