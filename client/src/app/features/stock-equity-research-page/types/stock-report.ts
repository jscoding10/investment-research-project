export interface StockReport {
  ticker: string;
  sentiment_analysis: {
    fundamental: string;
    technical: string;
    macro: string;
    industry: string;
    news: string;
    peer: string;
  };
  combined_sentiment: string;
}
