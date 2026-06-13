'use client';

import { useState, useRef } from 'react';

export default function InputForm({ onSubmit }) {
  const [productImages, setProductImages] = useState([]);
  const [productPreviews, setProductPreviews] = useState([]);
  const [licenseImage, setLicenseImage] = useState(null);
  const [licensePreview, setLicensePreview] = useState('');
  const [draggingProduct, setDraggingProduct] = useState(false);
  const [draggingLicense, setDraggingLicense] = useState(false);
  const [form, setForm] = useState({
    height: '',
    width: '',
    weight: '',
    description: '',
    platform: '',
    productNameHint: '',
    productMaterialHint: '',
  });
  const productInputRef = useRef(null);
  const licenseInputRef = useRef(null);

  function addProductFiles(files) {
    if (!files) return;
    const remaining = 4 - productImages.length;
    if (remaining <= 0) return;
    const added = [];
    const previews = [];
    Array.from(files)
      .slice(0, remaining)
      .forEach((f) => {
        if (f.type.startsWith('image/')) {
          added.push(f);
          previews.push(URL.createObjectURL(f));
        }
      });
    setProductImages((p) => [...p, ...added]);
    setProductPreviews((p) => [...p, ...previews]);
  }

  function removeProductImage(idx) {
    setProductImages((p) => p.filter((_, i) => i !== idx));
    setProductPreviews((p) => p.filter((_, i) => i !== idx));
  }

  function setLicenseFile(file) {
    if (!file) { setLicenseImage(null); setLicensePreview(''); return; }
    if (!file.type.startsWith('image/')) return;
    setLicenseImage(file);
    setLicensePreview(URL.createObjectURL(file));
  }

  function handleProductDrop(e) {
    e.preventDefault();
    setDraggingProduct(false);
    addProductFiles(e.dataTransfer.files);
  }

  function handleLicenseDrop(e) {
    e.preventDefault();
    setDraggingLicense(false);
    const file = e.dataTransfer.files?.[0] ?? null;
    setLicenseFile(file);
  }

  function handleChange(e) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      productImages,
      licenseImage,
      height: form.height,
      width: form.width,
      weight: form.weight,
      description: form.description,
      platform: form.platform,
      productNameHint: form.productNameHint || undefined,
      productMaterialHint: form.productMaterialHint || undefined,
    });
  }

  const isValid =
    productImages.length > 0 &&
    form.height.trim() !== '' &&
    form.width.trim() !== '' &&
    form.weight.trim() !== '' &&
    form.description.trim() !== '' &&
    form.platform !== '';

  return (
    <div style={{ maxWidth: 860, margin: '0 auto' }}>
      {/* Hero */}
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '6px 16px', borderRadius: 999, border: '1px solid var(--border)', background: 'var(--violet-glow-soft)', marginBottom: 20 }}>
          <span>✨</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--violet-300)', fontWeight: 600 }}>AI-Powered Product Launch</span>
        </div>
        <h2 style={{ fontSize: 'clamp(2rem, 4vw, 3rem)', fontWeight: 900, letterSpacing: '-0.04em', lineHeight: 1.1, marginBottom: 16 }}>
          Launch Your Product<br />
          <span className="gradient-text">Smarter &amp; Faster</span>
        </h2>
        <p style={{ maxWidth: 520, margin: '0 auto', fontSize: '1.05rem' }}>
          Upload your product images and enter details. Our AI generates optimised listings, packaging designs, and pricing insights in seconds.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="glass-card" style={{ marginBottom: 20 }}>
          <div className="card-body">
            {/* Product Images */}
            <div style={{ marginBottom: 24 }}>
              <div className="section-heading">
                <div className="section-icon">📦</div>
                <span className="section-title">Product Images</span>
                <span className="badge badge-violet">{productImages.length}/4</span>
              </div>
              <div
                id="product-image-drop"
                className={`upload-zone${draggingProduct ? ' dragging' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDraggingProduct(true); }}
                onDragLeave={() => setDraggingProduct(false)}
                onDrop={handleProductDrop}
                onClick={() => productImages.length < 4 && productInputRef.current?.click()}
                style={{ cursor: productImages.length >= 4 ? 'not-allowed' : 'pointer' }}
              >
                <input
                  ref={productInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  style={{ display: 'none' }}
                  onChange={(e) => addProductFiles(e.target.files)}
                  disabled={productImages.length >= 4}
                />
                <div className="upload-icon">🖼️</div>
                <p className="upload-label">
                  <strong>Click or drag</strong> product images here
                </p>
                <p className="upload-hint">Up to 4 images • JPG, PNG, WEBP</p>
              </div>
              {productPreviews.length > 0 && (
                <div className="upload-previews" style={{ marginTop: 12 }}>
                  {productPreviews.map((src, i) => (
                    <div key={i} className="upload-thumb">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={src} alt={`Product ${i + 1}`} />
                      <button
                        type="button"
                        className="upload-thumb-remove"
                        onClick={() => removeProductImage(i)}
                        title="Remove"
                      >×</button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* License Image */}
            <div>
              <div className="section-heading">
                <div className="section-icon">🔏</div>
                <span className="section-title">License / Certificate Image</span>
                <span className="badge badge-violet">Optional</span>
              </div>
              <div
                id="license-image-drop"
                className={`upload-zone${draggingLicense ? ' dragging' : ''}`}
                onDragOver={(e) => { e.preventDefault(); setDraggingLicense(true); }}
                onDragLeave={() => setDraggingLicense(false)}
                onDrop={handleLicenseDrop}
                onClick={() => licenseInputRef.current?.click()}
              >
                <input
                  ref={licenseInputRef}
                  type="file"
                  accept="image/*"
                  style={{ display: 'none' }}
                  onChange={(e) => setLicenseFile(e.target.files?.[0] ?? null)}
                />
                {licensePreview ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={licensePreview} alt="License" style={{ width: 64, height: 64, objectFit: 'cover', borderRadius: 8, border: '1px solid var(--border)' }} />
                    <div style={{ textAlign: 'left' }}>
                      <p style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 600 }}>{licenseImage?.name}</p>
                      <button type="button" style={{ fontSize: '0.75rem', color: 'var(--red-warn)', background: 'none', border: 'none', cursor: 'pointer', padding: 0, marginTop: 4 }} onClick={(e) => { e.stopPropagation(); setLicenseFile(null); }}>Remove</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="upload-icon">📄</div>
                    <p className="upload-label"><strong>Click or drag</strong> license image here</p>
                    <p className="upload-hint">FSSAI, Trademark, ISO, etc.</p>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Product Details */}
        <div className="glass-card" style={{ marginBottom: 20 }}>
          <div className="card-body">
            <div className="section-heading">
              <div className="section-icon">📝</div>
              <span className="section-title">Product Details</span>
            </div>
            <div className="form-grid">
              {/* Platform */}
              <div className="field-group form-full">
                <label className="field-label" htmlFor="platform">Platform <span className="required">*</span></label>
                <select
                  id="platform"
                  name="platform"
                  className="field-select"
                  value={form.platform}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select a marketplace...</option>
                  <option value="amazon">🛒 Amazon</option>
                  <option value="flipkart">🔵 Flipkart</option>
                  <option value="meesho">💜 Meesho</option>
                </select>
              </div>

              {/* Description */}
              <div className="field-group form-full">
                <label className="field-label" htmlFor="description">Product Description <span className="required">*</span></label>
                <textarea
                  id="description"
                  name="description"
                  className="field-textarea"
                  placeholder="Describe your product — material, use case, key features..."
                  value={form.description}
                  onChange={handleChange}
                  required
                />
              </div>

              {/* Dimensions */}
              <div className="field-group">
                <label className="field-label" htmlFor="height">Height <span className="required">*</span></label>
                <div style={{ position: 'relative' }}>
                  <input id="height" name="height" type="number" min="0" step="any" className="field-input" placeholder="e.g. 20" value={form.height} onChange={handleChange} required style={{ paddingRight: 48 }} />
                  <span style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600 }}>cm</span>
                </div>
              </div>

              <div className="field-group">
                <label className="field-label" htmlFor="width">Width <span className="required">*</span></label>
                <div style={{ position: 'relative' }}>
                  <input id="width" name="width" type="number" min="0" step="any" className="field-input" placeholder="e.g. 15" value={form.width} onChange={handleChange} required style={{ paddingRight: 48 }} />
                  <span style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600 }}>cm</span>
                </div>
              </div>

              <div className="field-group">
                <label className="field-label" htmlFor="weight">Weight <span className="required">*</span></label>
                <div style={{ position: 'relative' }}>
                  <input id="weight" name="weight" type="number" min="0" step="any" className="field-input" placeholder="e.g. 0.5" value={form.weight} onChange={handleChange} required style={{ paddingRight: 40 }} />
                  <span style={{ position: 'absolute', right: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 600 }}>kg</span>
                </div>
              </div>

              {/* Optional hints */}
              <div className="field-group">
                <label className="field-label" htmlFor="productNameHint">Product Name Hint</label>
                <input id="productNameHint" name="productNameHint" type="text" className="field-input" placeholder="e.g. Wooden serving tray" value={form.productNameHint} onChange={handleChange} />
              </div>

              <div className="field-group form-full">
                <label className="field-label" htmlFor="productMaterialHint">Material Hint</label>
                <input id="productMaterialHint" name="productMaterialHint" type="text" className="field-input" placeholder="e.g. Bamboo, Stainless Steel..." value={form.productMaterialHint} onChange={handleChange} />
              </div>
            </div>
          </div>
        </div>

        <button
          id="submit-workflow"
          type="submit"
          className="btn-primary"
          disabled={!isValid}
          style={{ fontSize: '1.05rem', padding: '16px 32px' }}
        >
          <span>🚀</span>
          Generate Full Product Package
        </button>
      </form>
    </div>
  );
}
