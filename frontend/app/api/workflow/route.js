import { NextResponse } from 'next/server';

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://127.0.0.1:8000';

export async function POST(req) {
  try {
    const body = await req.formData();

    const backendRes = await fetch(`${BACKEND}/api/full-workflow`, {
      method: 'POST',
      body: body,
      // Do NOT set Content-Type — fetch sets multipart/form-data with boundary automatically
    });

    const data = await backendRes.json();
    return NextResponse.json(data, { status: backendRes.status });
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Proxy error';
    return NextResponse.json({ detail: `Proxy error: ${message}` }, { status: 502 });
  }
}
