export interface RealEstateRequest {
  address: string;
  purchase_price: number;
  down_payment_pct: number;
  loan_term_years: number;
  interest_rate: number;
  estimated_rent: number;
  time_horizon_years: number;
}
