'use client';

import { resolveImageUrl } from '@/lib/api';

export default function ResultsDashboard({ data }) {

  const { platform, product_analysis, listing, images, packaging, license_analysis, pricing, disclaimers } = data;



  /* ✅ IMAGE NORMALIZATION FROM FIRST CODE */
  const originalImages =
    images?.original_images?.length
      ? images.original_images
      : images?.original_image
        ? [images.original_image]
        : [];

  const cleanedImages =
    images?.cleaned_images?.length
      ? images.cleaned_images
      : images?.cleaned_image
        ? [images.cleaned_image]
        : [];

  const handleDownload = async (url, defaultName) => {
    try {
      const resolvedUrl = resolveImageUrl(url);
      const response = await fetch(resolvedUrl);
      if (!response.ok) throw new Error('Network response was not ok');
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      
      // Determine file extension and name
      let filename = defaultName;
      if (url) {
        const parts = url.split(/[/\\]/);
        const lastPart = parts[parts.length - 1];
        if (lastPart && lastPart.includes('.')) {
          filename = lastPart;
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Failed to download image:', error);
      // Fallback: open in new tab
      const resolvedUrl = resolveImageUrl(url);
      window.open(resolvedUrl, '_blank');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* ── Row 1: Platform Rules + Product Info ── */}
      <div className="results-grid">

        {/* Platform Rules */}
        <div className="glass-card">
          <div className="card-body">

            <div className="section-heading">
              <div className="section-icon">🏪</div>
              <div>
                <p className="section-title" style={{ textTransform: 'capitalize' }}>
                  {platform.selected} Platform Rules
                </p>
              </div>
            </div>

            {platform.rules_summary.listing_rules.length > 0 && (
              <>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Listing Rules</p>
                <ul className="rule-list" style={{ marginBottom: 14 }}>
                  {platform.rules_summary.listing_rules.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </>
            )}

            {platform.rules_summary.image_rules.length > 0 && (
              <>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Image Rules</p>
                <ul className="rule-list" style={{ marginBottom: 14 }}>
                  {platform.rules_summary.image_rules.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </>
            )}

            {platform.rules_summary.compliance_notes.length > 0 && (
              <>
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>Compliance Notes</p>
                <ul className="rule-list">
                  {platform.rules_summary.compliance_notes.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </>
            )}

            {platform.rules_summary.disclaimer && (
              <div style={{ marginTop: 14, padding: '10px 12px', borderRadius: 8, background: 'rgba(251,191,36,0.08)', border: '1px solid rgba(251,191,36,0.2)', fontSize: '0.78rem', color: 'var(--amber-caution)' }}>
                ⚠️ {platform.rules_summary.disclaimer}
              </div>
            )}

          </div>
        </div>

        {/* Product Analysis */}
        <div className="glass-card">
          <div className="card-body">

            <div className="section-heading">
              <div className="section-icon">🛍️</div>
              <span className="section-title">Product Analysis</span>
            </div>

            <div>
              <div className="info-row">
                <span className="info-key">Identified as</span>
                <span className="info-val">{product_analysis.identified_product || '—'}</span>
              </div>

              <div className="info-row">
                <span className="info-key">Category</span>
                <span className="info-val">{product_analysis.category?.platform_category || '—'}</span>
              </div>

              <div className="info-row">
                <span className="info-key">Sub-category</span>
                <span className="info-val">{product_analysis.category?.platform_subcategory || '—'}</span>
              </div>

              <div className="info-row">
                <span className="info-key">Material</span>
                <span className="info-val">{product_analysis.attributes?.material || '—'}</span>
              </div>

              <div className="info-row">
                <span className="info-key">Color</span>
                <span className="info-val">{product_analysis.attributes?.color || '—'}</span>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* ── Row 2: Listing ── */}
      <div className="glass-card">
        <div className="card-body">

          <div className="section-heading">
            <div className="section-icon">📝</div>
            <span className="section-title">Marketplace Listing</span>
          </div>

          <h3 style={{ fontSize: '1.3rem', fontWeight: 800, letterSpacing: '-0.02em', marginBottom: 12 }}>
            {listing.title || 'No title generated'}
          </h3>

          <p style={{ fontSize: '0.9rem', lineHeight: 1.75, marginBottom: 20 }}>
            {listing.description || 'No description generated'}
          </p>

        </div>
      </div>

      {/* ── Row 3: Images (FROM FIRST CODE) ── */}
      {(originalImages.length > 0 || cleanedImages.length > 0 || packaging.packaging_mockup_image_url) && (
        <div className="glass-card">
          <div className="card-body">

            <div className="section-heading">
              <div className="section-icon">🖼️</div>
              <span className="section-title">Images</span>
            </div>

            {originalImages.length > 0 && (
              <>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: 12 }}>Original</p>
                <div className="image-grid" style={{ marginBottom: 20 }}>
                  {originalImages.map((url, i) => (
                    <div key={i} className="image-card">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={resolveImageUrl(url)} alt={`Original ${i + 1}`} />
                      <button 
                        className="image-card-action" 
                        onClick={() => handleDownload(url, `original-${i + 1}.png`)}
                        title="Download original image"
                        aria-label="Download original image"
                      >
                        <svg 
                          xmlns="http://www.w3.org/2000/svg" 
                          width="16" 
                          height="16" 
                          viewBox="0 0 24 24" 
                          fill="none" 
                          stroke="currentColor" 
                          strokeWidth="2.5" 
                          strokeLinecap="round" 
                          strokeLinejoin="round"
                        >
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                          <polyline points="7 10 12 15 17 10" />
                          <line x1="12" y1="15" x2="12" y2="3" />
                        </svg>
                      </button>
                      <span className="image-card-label">Original {i + 1}</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {cleanedImages.length > 0 && (
              <>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: 12 }}>AI Enhanced</p>
                <div className="image-grid" style={{ marginBottom: 20 }}>
                  {cleanedImages.map((url, i) => (
                    <div key={i} className="image-card">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={resolveImageUrl(url)} alt={`Enhanced ${i + 1}`} />
                      <button 
                        className="image-card-action" 
                        onClick={() => handleDownload(url, `enhanced-${i + 1}.png`)}
                        title="Download enhanced image"
                        aria-label="Download enhanced image"
                      >
                        <svg 
                          xmlns="http://www.w3.org/2000/svg" 
                          width="16" 
                          height="16" 
                          viewBox="0 0 24 24" 
                          fill="none" 
                          stroke="currentColor" 
                          strokeWidth="2.5" 
                          strokeLinecap="round" 
                          strokeLinejoin="round"
                        >
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                          <polyline points="7 10 12 15 17 10" />
                          <line x1="12" y1="15" x2="12" y2="3" />
                        </svg>
                      </button>
                      <span className="image-card-label">Enhanced {i + 1}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
            {packaging?.packaging_mockup_image_url && (
              <>
                <p
                  style={{
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    marginBottom: 12
                  }}
                >
                  Packaging Page
                </p>

                <div className="image-grid">
                  <div className="image-card"
                    style={{
                      background: "#ffffff",
                      borderRadius: 16,
                      overflow: "hidden",
                      border: "1px solid rgba(255,255,255,0.12)",
                      height: "500px"
                    }}
                  >
                    <iframe
                      src={`https://www.templatemaker.nl/en/${packaging.recommended_packaging_type}/`}
                      width="100%"
                      height="100%"
                      style={{ border: "none", borderRadius: "12px" }}
                    />
                  </div>
                </div>
              </>
            )}

          </div>
        </div>
      )}

      {/* ── Row 4: Packaging + License ── */}
      <div className="results-grid">

        {/* Packaging */}
        <div className="glass-card">
          <div className="card-body">

            <div className="section-heading">
              <div className="section-icon">📦</div>
              <span className="section-title">Packaging Design</span>
            </div>

            <div>
              <div className="info-row">
                <span className="info-key">Type</span>
                <span className="info-val">
                  {packaging.recommended_packaging_type || '—'}
                </span>
              </div>

              <div className="info-row">
                <span className="info-key">Material</span>
                <span className="info-val">
                  {packaging.packaging_material || '—'}
                </span>
              </div>

              <div className="info-row">
                <span className="info-key">Height</span>
                <span className="info-val">
                  {packaging.packaging_dimensions?.height ?? '—'}{' '}
                  {packaging.packaging_dimensions?.unit || 'cm'}
                </span>
              </div>

              <div className="info-row">
                <span className="info-key">Width</span>
                <span className="info-val">
                  {packaging.packaging_dimensions?.width ?? '—'}{' '}
                  {packaging.packaging_dimensions?.unit || 'cm'}
                </span>
              </div>

              {packaging.packaging_dimensions?.weight_support_note && (
                <div className="info-row">
                  <span className="info-key">Weight Note</span>
                  <span className="info-val">
                    {packaging.packaging_dimensions.weight_support_note}
                  </span>
                </div>
              )}

              {packaging.dieline_template_status && (
                <div className="info-row">
                  <span className="info-key">Dieline Status</span>
                  <span className="info-val">
                    {packaging.dieline_template_status}
                  </span>
                </div>
              )}
            </div>

            {packaging.design_notes?.length > 0 && (
              <>
                <div className="divider" />

                <p
                  style={{
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                    marginBottom: 10
                  }}
                >
                  Design Notes
                </p>

                <ul className="bullet-list">
                  {packaging.design_notes.map((n, i) => (
                    <li key={i}>{n}</li>
                  ))}
                </ul>
              </>
            )}

            {packaging.dieline_download_url && (
              <div style={{ marginTop: 16 }}>
                <a
                  href={packaging.dieline_download_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary"
                  style={{ display: 'inline-flex', textDecoration: 'none' }}
                >
                  ⬇️ Download Dieline Template
                </a>
              </div>
            )}

          </div>
        </div>


        {/* License */}
        <div className="glass-card">
          <div className="card-body">

            <div className="section-heading">
              <div className="section-icon">🔏</div>
              <span className="section-title">License Analysis</span>
              <LicenseBadge confidence={license_analysis.confidence} />
            </div>

            <div>

              <div className="info-row">
                <span className="info-key">Document Type</span>
                <span className="info-val">
                  {license_analysis.document_type || 'Not provided'}
                </span>
              </div>

              <div className="info-row">
                <span className="info-key">Issuing Authority</span>
                <span className="info-val">
                  {license_analysis.issuing_authority || '—'}
                </span>
              </div>

              {license_analysis.license_numbers?.length > 0 && (
                <div className="info-row">
                  <span className="info-key">License Numbers</span>
                  <span className="info-val">
                    {license_analysis.license_numbers.join(', ')}
                  </span>
                </div>
              )}

              <div className="info-row">
                <span className="info-key">Product Match</span>
                <span
                  className="info-val"
                  style={{ color: 'var(--violet-300)' }}
                >
                  {license_analysis.product_match_assessment || '—'}
                </span>
              </div>

            </div>

            <div className="divider" />

            <p
              style={{
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                marginBottom: 8
              }}
            >
              Confidence
            </p>

            <div className="confidence-bar-wrap">

              <div className="confidence-bar-bg">
                <div
                  className="confidence-bar-fill"
                  style={{
                    width: `${Math.round(
                      (license_analysis.confidence || 0) * 100
                    )}%`
                  }}
                />
              </div>

              <span className="confidence-pct">
                {Math.round((license_analysis.confidence || 0) * 100)}%
              </span>

            </div>

            {license_analysis.warnings?.length > 0 && (
              <>
                <div className="divider" />

                <p
                  style={{
                    fontSize: '0.75rem',
                    color: 'var(--amber-caution)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                    marginBottom: 8
                  }}
                >
                  ⚠️ Warnings
                </p>

                <ul className="bullet-list">
                  {license_analysis.warnings.map((w, i) => (
                    <li
                      key={i}
                      style={{ color: 'var(--amber-caution)' }}
                    >
                      {w}
                    </li>
                  ))}
                </ul>
              </>
            )}

            {license_analysis.disclaimer && (
              <p
                style={{
                  marginTop: 14,
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                  fontStyle: 'italic'
                }}
              >
                {license_analysis.disclaimer}
              </p>
            )}


          </div>
        </div>

      </div>
      {/* ── Row 5: Pricing ── */}
      {pricing && (
        <div className="glass-card">
          <div className="card-body">

            <div className="section-heading">
              <div className="section-icon">💰</div>
              <span className="section-title">Price Suggestion</span>
              <span className="badge badge-violet">{pricing.currency}</span>
            </div>

            <div className="price-range-row">

              <div>
                <p className="price-label">Min</p>
                <p className="price-amount">
                  ₹{pricing.estimated_price_range?.min?.toLocaleString() ?? '—'}
                </p>
              </div>

              <span className="price-sep">–</span>

              <div>
                <p className="price-label">Max</p>
                <p className="price-amount">
                  ₹{pricing.estimated_price_range?.max?.toLocaleString() ?? '—'}
                </p>
              </div>

              <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                <p className="price-label">Suggested Sweet Spot</p>
                <p
                  style={{
                    fontSize: '1.1rem',
                    fontWeight: 700,
                    color: 'var(--green-ok)'
                  }}
                >
                  ₹
                  {pricing.estimated_price_range
                    ? Math.round(
                      (pricing.estimated_price_range.min +
                        pricing.estimated_price_range.max) / 2
                    ).toLocaleString()
                    : '—'}
                </p>
              </div>

            </div>

            {/* Competitors */}
            {pricing.example_competitors?.length > 0 && (
              <>
                <p
                  style={{
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                    marginBottom: 12
                  }}
                >
                  Competitor Benchmarks
                </p>

                <table className="comp-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th>Price</th>
                      <th>Source</th>
                    </tr>
                  </thead>

                  <tbody>
                    {pricing.example_competitors.map((c, i) => (
                      <tr key={i}>
                        <td style={{ color: 'var(--text-primary)', maxWidth: 280 }}>
                          {c.url ? (
                            <a
                              href={c.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="comp-link"
                            >
                              {c.title}
                            </a>
                          ) : (
                            c.title
                          )}
                        </td>

                        <td
                          style={{
                            color: 'var(--violet-300)',
                            fontWeight: 700
                          }}
                        >
                          ₹{c.price?.toLocaleString()}
                        </td>

                        <td style={{ color: 'var(--text-muted)' }}>
                          {c.source}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}

          </div>
        </div>
      )}


      {/* ── Disclaimers ── */}
      {disclaimers?.length > 0 && (
        <div
          style={{
            padding: '16px 20px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border)',
            background: 'rgba(13,13,20,0.6)'
          }}
        >
          <p
            style={{
              fontSize: '0.75rem',
              color: 'var(--text-muted)',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              marginBottom: 8
            }}
          >
            Disclaimers
          </p>

          {disclaimers.map((d, i) => (
            <p
              key={i}
              style={{
                fontSize: '0.78rem',
                color: 'var(--text-muted)',
                marginBottom: 4
              }}
            >
              • {d}
            </p>
          ))}
        </div>
      )}


    </div>
  );
}

function LicenseBadge({ confidence }) {
  const pct = Math.round((confidence || 0) * 100);
  if (pct >= 70) return <span className="badge badge-green">✓ Approved</span>;
  if (pct >= 40) return <span className="badge badge-amber">⚠ Review</span>;
  return <span className="badge badge-red">✗ Low Confidence</span>;
}