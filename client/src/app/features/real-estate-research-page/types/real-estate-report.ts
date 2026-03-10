export interface RealEstateReport {
  address: string;
  analysis: {
    market: string;
    financial: string;
    risk: string;
  };
  combined_analysis: string;
}
