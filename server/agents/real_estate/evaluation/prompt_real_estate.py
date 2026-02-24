sentiment_evaluator_prompt = """
Real estate sentiment output should:
1. Resummarize the key findings from each research agent (2-3 sentences each)
2. Identify areas of consensus and divergence across the different analyses
3. Weight the importance of each perspective based on the property characteristics and market conditions
4. Synthesize all findings into a clear, cohesive overall investment recommendation

Response should be in Markdown as follows (do not use JSON):

**Summary of Research Findings:**
- Financial: [key takeaways]
- Market Trends: [key takeaways]
- Risk Assessment: [key takeaways]

Consensus and Divergence:
- Consensus: [content]  
- Divergence: [content]

Weighting of Perspectives:
- Financial [percentage and explanation] 
- Market Trends [percentage and explanation] 
- Risk Assessment [percentage and explanation]

**Overall Recommendation:** [STRONG BUY / HOLD / AVOID]

**Conclusion:** [3-4 sentences synthesizing the most important factors driving your overall recommendation for the property, 
acknowledging any conflicting signals, and providing a balanced perspective on the investment opportunity]

Entire response should be under 400 words, and should be decisive yet acknowledge uncertainty where appropriate.
"""