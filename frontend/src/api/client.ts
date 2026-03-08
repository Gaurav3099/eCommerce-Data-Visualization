import type { ApiData, CategoriesResponse } from '../types/api';

const API_BASE = '/api';

export async function fetchData(params: {
  nrows?: number;
  categories?: string[];
}): Promise<ApiData> {
  const search = new URLSearchParams();
  if (params.nrows != null) search.set('nrows', String(params.nrows));
  if (params.categories?.length)
    search.set('categories', params.categories.join(','));
  const url = `${API_BASE}/data${search.toString() ? '?' + search : ''}`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail || 'Failed to fetch data');
  }
  return res.json();
}

export async function fetchCategories(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/categories`);
  const data: CategoriesResponse = await res.json();
  if (data.error) throw new Error(data.error);
  return data.categories || [];
}
