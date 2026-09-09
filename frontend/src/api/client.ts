const rawHost = (import.meta as any).env?.VITE_API_BASE_URL || '';
const API_HOST = typeof rawHost === 'string' ? rawHost.replace(/\/$/, '') : '';
const BASE_URL = `${API_HOST}/api/v1`;

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers: options.body instanceof FormData ? options.headers : headers,
    });
  } catch (err: any) {
    throw new Error(
      'Cannot reach FactLens backend. If the backend is waking up on Render, please wait 30 seconds and refresh. For local usage, run the FastAPI backend at http://127.0.0.1:8000.'
    );
  }


  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `API error: ${response.status}`);
  }

  const json = await response.json();
  return json.data !== undefined ? json.data : json;
}
