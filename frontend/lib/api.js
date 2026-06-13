export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';

// ─── API call ─────────────────────────────────────────────────────────────────

export async function submitWorkflow(values) {
  const form = new FormData();

  // Product images mapped to backend field names
  const imageFieldNames = ['product_image', 'product_image_2', 'product_image_3', 'product_image_4'];
  values.productImages.slice(0, 4).forEach((file, i) => {
    form.append(imageFieldNames[i], file);
  });

  if (values.licenseImage) form.append('license_image', values.licenseImage);

  form.append('height', values.height);
  form.append('width', values.width);
  // Backend weight_unit defaults to 'g', but user enters kg — convert
  const weightG = (parseFloat(values.weight) * 1000).toString();
  form.append('weight', weightG);
  form.append('weight_unit', 'g');
  form.append('dimension_unit', 'cm');
  form.append('description', values.description);
  form.append('platform', values.platform);
  if (values.productNameHint) form.append('product_name_hint', values.productNameHint);
  if (values.productMaterialHint) form.append('product_material_hint', values.productMaterialHint);

  // Send the request to our Next.js server-side proxy route.
  // This avoids all browser CORS issues since it's on the same origin (localhost:3000).
  const response = await fetch('/api/workflow', {
    method: 'POST',
    body: form,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Unknown error' }));
    const detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
    throw new Error(detail || `Server error ${response.status}`);
  }

  return response.json();
}

// ─── Image URL helper ─────────────────────────────────────────────────────────

/**
 * Paths can be either:
 *  - a relative path like "uploads/foo.jpg"  → prepend backend URL
 *  - an absolute URL (cloudinary / http)      → use as-is
 */
export function resolveImageUrl(path) {
  if (!path) return "";

  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  const normalized = path.replace(/\\/g, "/");

  // New: support backend API image proxy routes like /api/packaging/mockup/giftbox
  if (normalized.startsWith("/api/")) {
    return `${BACKEND_URL}${normalized}`;
  }

  const uploadsIndex = normalized.lastIndexOf("/uploads/");
  if (uploadsIndex !== -1) {
    const relativePath = normalized.substring(uploadsIndex + "/uploads/".length);
    return `${BACKEND_URL}/uploads/${relativePath}`;
  }

  const originalIndex = normalized.lastIndexOf("/original/");
  if (originalIndex !== -1) {
    const relativePath = normalized.substring(originalIndex + 1);
    return `${BACKEND_URL}/uploads/${relativePath}`;
  }

  const cleanedIndex = normalized.lastIndexOf("/cleaned/");
  if (cleanedIndex !== -1) {
    const relativePath = normalized.substring(cleanedIndex + 1);
    return `${BACKEND_URL}/uploads/${relativePath}`;
  }

  const filename = normalized.split("/").pop() || "";
  return filename ? `${BACKEND_URL}/uploads/${filename}` : "";
}