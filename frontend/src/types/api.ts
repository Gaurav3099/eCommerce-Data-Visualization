export interface RevenueByMonth {
  month: string;
  revenue: number;
  transactions?: number;
}

export interface ConversionFunnelStage {
  stage: string;
  users: number;
  sessions: number;
  events: number;
}

export interface CustomerSegment {
  segment: string;
  users: number;
  revenue: number;
}

export interface TopCategory {
  category: string;
  revenue: number;
  transactions?: number;
}

export interface PivotData {
  rows: string[];
  columns: string[];
  data: number[][];
}

export interface ApiData {
  revenue_by_day: { date: string; revenue: number }[];
  revenue_by_month: RevenueByMonth[];
  conversion_funnel: ConversionFunnelStage[];
  customer_segments: CustomerSegment[];
  top_categories_revenue: TopCategory[];
  top_categories_events: { category: string; events: number }[];
  heatmap_hour_dow: PivotData;
  heatmap_category_month: PivotData;
  cohort_retention: PivotData;
  error?: string;
}

export interface CategoriesResponse {
  categories: string[];
  error?: string;
}
