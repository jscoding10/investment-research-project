export interface CryptoReport {
  ticker: string;
  sentiment_analysis: {
    technical: string;
    macro: string;
    news: string;
    peer: string;
  };
  combined_sentiment: string;
}
