// Angular
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

// Libraries
import { MarkdownModule } from 'ngx-markdown';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
import type { TDocumentDefinitions, Content, StyleDictionary } from 'pdfmake/interfaces';
import { TooltipModule } from 'primeng/tooltip';

// Application
import { StockReport } from '../../state/stock-state';
import { StockEquityResearchStateService } from '../../services/stock-equity-research-state.service';

@Component({
  selector: 'app-stock-equity-research-report',
  imports: [CommonModule, MarkdownModule, TooltipModule],
  templateUrl: './stock-equity-research-report.component.html',
  styleUrl: './stock-equity-research-report.component.css',
})
export class StockEquityResearchReportComponent {
  private state = inject(StockEquityResearchStateService);

  report = this.state.report;
  isLoading = this.state.isLoading;
  ticker = this.state.ticker;
  error = this.state.error;

  private pdfMakeInstance: any = null;

  private parser: any = null;

  private getParser() {
    if (!this.parser) {
      this.parser = unified().use(remarkParse).use(remarkGfm);
    }
    return this.parser;
  }

  getOverallReport(report: StockReport | null): string {
    if (!report) return 'NEUTRAL';
    const match = report.combined_sentiment.match(/Overall Sentiment: (\w+)/);
    return match ? (match[1] as 'BULLISH' | 'BEARISH' | 'NEUTRAL') : 'NO REPORT';
  }

  getOverallSentiment(report: StockReport): 'BULLISH' | 'BEARISH' | 'NEUTRAL' {
    const text = report.combined_sentiment.toUpperCase();

    if (text.includes('OVERALL SENTIMENT: BULLISH') || text.includes('**OVERALL SENTIMENT:** BULLISH')) {
      return 'BULLISH';
    }
    if (text.includes('OVERALL SENTIMENT: BEARISH') || text.includes('**OVERALL SENTIMENT:** BEARISH')) {
      return 'BEARISH';
    }
    if (text.includes('BULLISH')) return 'BULLISH';
    if (text.includes('BEARISH')) return 'BEARISH';

    return 'NEUTRAL';
  }

  // // Convert Markdown
  // private mdToContent(md: string): Content[] {
  //   const lines = md.split('\n');
  //   const content: Content[] = [];
  //   let currentParagraph: (string | { text: string; bold: true })[] = [];

  //   const formatParagraph = () => {
  //     if (currentParagraph.length > 0) {
  //       content.push({ text: currentParagraph, margin: [0, 6, 0, 6] });
  //       currentParagraph = [];
  //     }
  //   };

  //   for (const line of lines) {
  //     const trimmed = line.trim();

  //     if (trimmed === '') {
  //       formatParagraph();
  //       continue;
  //     }

  //     if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
  //       formatParagraph();
  //       const bulletText = trimmed.slice(2);
  //       const parts = bulletText.split(/\*\*(.+?)\*\*/g);
  //       const inline: (string | { text: string; bold: true })[] = [];
  //       for (let i = 0; i < parts.length; i++) {
  //         if (i % 2 === 0) {
  //           if (parts[i]) inline.push(parts[i]);
  //         } else {
  //           inline.push({ text: parts[i], bold: true });
  //         }
  //       }
  //       content.push({ text: inline, margin: [10, 2, 0, 2] });
  //     } else {
  //       // Accumulate paragraph lines
  //       const parts = line.split(/\*\*(.+?)\*\*/g);
  //       for (let i = 0; i < parts.length; i++) {
  //         if (i % 2 === 0) {
  //           if (parts[i]) currentParagraph.push(parts[i]);
  //         } else {
  //           currentParagraph.push({ text: parts[i], bold: true });
  //         }
  //       }
  //       currentParagraph.push(' '); // Preserve spacing
  //     }
  //   }

  //   formatParagraph();
  //   return content;
  // }

  private normalizeMarkdown(md: string): string {
    if (!md) return '';

    return (
      md
        // Fix problematic invisible/Unicode characters from Large Language Models
        .replace(/\u202F/g, ' ') // Narrow no-break space → regular space
        .replace(/\u2011/g, '-') // Non-breaking hyphen → regular hyphen
        .replace(/[\u2013\u2014]/g, '-') // en-dash/em-dash → regular dash
        .replace(/[\u201C\u201D]/g, '"') // Fancy quotes → straight
        .replace(/[\u2018\u2019]/g, "'")

        // Fix ≈ (almost equal to)
        .replace(/\u2248/g, '~') // ≈ → ~ (standard in finance for "approximately")

        // Prevent line breaks in ANY financial ratio with slash
        // Matches patterns like: P/E, EV/EBITDA, PEG, P/B, P/S, EV/Sales, etc.
        .replace(/\b([A-Z]{1,6})\/([A-Z]{1,6})\b/gi, '$1\u2044$2') // ⁄ = non-breaking fraction slash

        // Clean horizontal whitespace only (preserve newlines!)
        .replace(/[ \t]+/g, ' ')

        .trim()
    );
  }

  private mdToContent(md: string): Content[] {
    if (!md?.trim()) return [];

    const cleaned = this.normalizeMarkdown(md);
    const tree = this.getParser().parse(cleaned);

    const content: Content[] = [];

    const visit = (node: any): Content | Content[] | undefined => {
      switch (node.type) {
        case 'root':
          return node.children.flatMap(visit).filter(Boolean);

        case 'paragraph': {
          const paragraphContent: (string | { text: string; bold?: true; italics?: true })[] = [];
          node.children.forEach((child: any) => {
            if (child.type === 'text') {
              paragraphContent.push(child.value);
            } else if (child.type === 'strong') {
              paragraphContent.push({ text: child.children[0]?.value || '', bold: true });
            } else if (child.type === 'emphasis') {
              paragraphContent.push({ text: child.children[0]?.value || '', italics: true });
            }
          });

          if (paragraphContent.length > 0) {
            return {
              text: paragraphContent,
              margin: [0, 8, 0, 8],
              alignment: 'justify',
            };
          }
          return undefined; // Explicit return for empty paragraph
        }

        case 'heading': {
          const level = node.depth;
          const text = node.children.map((c: any) => c.value || '').join('');
          const fontSize = level === 1 ? 20 : level === 2 ? 18 : 16;

          if (text) {
            // Guard against empty headings
            return {
              text,
              style: 'sectionHeader',
              fontSize,
              margin: [0, 30, 0, 12],
              alignment: 'left',
            };
          }
          return undefined; // Explicit return for empty heading
        }

        case 'list': {
          const items: Content[] = [];

          node.children.forEach((item: any) => {
            const listItemContent: (string | { text: string; bold?: true; italics?: true })[] = [];

            if (item.children.length > 0) {
              item.children.forEach((child: any) => {
                if (child.type === 'paragraph') {
                  child.children.forEach((grachi: any) => {
                    if (grachi.type === 'text') {
                      listItemContent.push(grachi.value);
                    } else if (grachi.type === 'strong') {
                      listItemContent.push({ text: grachi.children[0]?.value || '', bold: true });
                    } else if (grachi.type === 'emphasis') {
                      listItemContent.push({ text: grachi.children[0]?.value || '', italics: true });
                    }
                  });
                }
              });
            }

            if (listItemContent.length > 0) {
              items.push({ text: listItemContent });
            } else {
              items.push({ text: '•' });
            }
          });

          // Key fix: use native pdfmake list + safe type assertion
          return {
            [node.ordered ? 'ol' : 'ul']: items,
            margin: [20, 6, 0, 10],
          } as unknown as Content;
        }

        default:
          if (node.value) {
            return { text: node.value, margin: [0, 8, 0, 8] };
          }
          return undefined; // Explicit return for unmatched defaults
      }
    };

    const result = tree.children.flatMap(visit).filter(Boolean) as Content[];
    return result;
  }

  private async loadPdfMake() {
    if (!this.pdfMakeInstance) {
      const pdfMakeLib = await import('pdfmake/build/pdfmake');
      this.pdfMakeInstance = pdfMakeLib.default;

      // Set Inter font via CDN TTF URLs (matches your Google Fonts; fixes VFS errors)
      this.pdfMakeInstance.fonts = {
        Inter: {
          normal: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-400-normal.woff',
          bold: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-700-normal.woff',
          italics: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-400-italic.woff',
          bolditalics: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-700-italic.woff',
        },
      };
    }
    return this.pdfMakeInstance;
  }

  // private async loadPdfMake(): Promise<any> {
  //   if (!this.pdfMakeInstance) {
  //     const pdfMakeModule = await import('pdfmake/build/pdfmake');
  //     this.pdfMakeInstance = pdfMakeModule; // namespace import

  //     // Use reliable Roboto fonts from official pdfmake CDN
  //     this.pdfMakeInstance.fonts = {
  //       Roboto: {
  //         normal: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-Regular.ttf',
  //         bold: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-Medium.ttf',
  //         italics: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-Italic.ttf',
  //         bolditalics: 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/fonts/Roboto/Roboto-MediumItalic.ttf',
  //       },
  //     };
  //   }
  //   return this.pdfMakeInstance;
  // }

  async exportToPDF() {
    if (!this.report()) return;

    const pdfMake = await this.loadPdfMake();
    const data = this.report()!;

    const sentiment = this.getOverallSentiment(data);

    const docDefinition: TDocumentDefinitions = {
      pageSize: 'A4',
      pageMargins: [40, 60, 40, 60],
      defaultStyle: {
        font: 'Inter', // Use your Inter font
        fontSize: 12,
        color: '#000000',
      },

      content: [
        {
          stack: [
            {
              text: `${data.ticker.toUpperCase()} Equity Research Report`,
              style: 'ticker',
            },
            // { text: sentiment, style: 'sentiment', alignment: 'center' },
            // { text: 'Equity Research Report', style: 'subheader', alignment: 'center' },
          ],
          margin: [0, 0, 0, 10],
        },

        // { text: 'Overall Conclusion', style: 'sectionHeader', fontSize: 16 },
        ...this.mdToContent(data.combined_sentiment),

        { text: '', pageBreak: 'after', margin: [0, 0, 0, 0] },

        // Full-width sections (no columns/cards)
        { text: 'Fundamental', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.fundamental), style: 'sentimentText' },
        // ...this.mdToContent(data.sentiment_analysis.fundamental),

        { text: 'Technical', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.technical), style: 'sentimentText' },

        { text: 'Peer Comparison', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.peer), style: 'sentimentText' },

        { text: 'Industry', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.industry), style: 'sentimentText' },

        { text: 'News & Sentiment', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.news), style: 'sentimentText' },

        { text: 'Macro Factors', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.macro), style: 'sentimentText' },
      ],

      styles: {
        ticker: { fontSize: 18, bold: true, color: '#000000' },
        sectionHeader: { fontSize: 16, bold: true, color: '#000000' },
        sentimentText: { fontSize: 12, color: '#000000', margin: [0, 0, 0, 10] },
      } as StyleDictionary,
    };

    const pdfDocGenerator = pdfMake.createPdf(docDefinition);
    pdfDocGenerator.getBlob((blob: Blob) => {
      const url = URL.createObjectURL(blob);
      window.open(url, '_blank');
      setTimeout(() => URL.revokeObjectURL(url), 10000);
    });
  }
}

// pdfMake.createPdf(docDefinition).download(`${this.ticker().toUpperCase()}_Equity_Research_Report.pdf`);
// Convert Markdown with inline bold handling
//   private mdToContent(md: string): Content[] {
//     const lines = md.split('\n');
//     const content: Content[] = [];
//     let currentParagraph = '';

//     const parseInlineBold = (text: string): (string | { text: string; bold: boolean })[] => {
//       const parts = text.split(/\*\*(.+?)\*\*/g); // Non-greedy match for inline bold
//       const spans: (string | { text: string; bold: boolean })[] = [];
//       for (let i = 0; i < parts.length; i++) {
//         if (i % 2 === 0) {
//           if (parts[i].trim()) spans.push(parts[i]);
//         } else {
//           spans.push({ text: parts[i], bold: true });
//         }
//       }
//       return spans;
//     };

//     for (const line of lines) {
//       const trimmed = line.trim();

//       if (trimmed === '') {
//         if (currentParagraph) {
//           content.push({ text: parseInlineBold(currentParagraph.trim()), margin: [0, 6, 0, 6] });
//           currentParagraph = '';
//         }
//       } else if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
//         if (currentParagraph) {
//           content.push({ text: parseInlineBold(currentParagraph.trim()), margin: [0, 6, 0, 6] });
//           currentParagraph = '';
//         }
//         content.push({ text: parseInlineBold(trimmed.slice(2)), margin: [10, 2, 0, 2] });
//       } else if (trimmed.startsWith('# ')) {
//         if (currentParagraph) {
//           content.push({ text: parseInlineBold(currentParagraph.trim()), margin: [0, 6, 0, 6] });
//           currentParagraph = '';
//         }
//         content.push({ text: trimmed.slice(2), style: 'header', margin: [0, 10, 0, 5] });
//       } else {
//         currentParagraph += ' ' + line; // Preserve original spacing
//       }
//     }

//     if (currentParagraph) {
//       content.push({ text: parseInlineBold(currentParagraph.trim()), margin: [0, 6, 0, 6] });
//     }

//     return content;
//   }

//   private async loadPdfMake() {
//     if (!this.pdfMakeInstance) {
//       const pdfMakeModule = await import('pdfmake/build/pdfmake');
//       this.pdfMakeInstance = pdfMakeModule;

//       // Set Inter font via CDN TTF URLs (matches your Google Fonts; fixes VFS errors)
//       this.pdfMakeInstance.fonts = {
//         Inter: {
//           normal: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-400-normal.ttf',
//           bold: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-700-normal.ttf',
//           italics: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-400-italic.ttf',
//           bolditalics: 'https://unpkg.com/@fontsource/inter@5.0.20/files/inter-latin-700-italic.ttf',
//         },
//       };
//     }
//     return this.pdfMakeInstance;
//   }

//   async exportToPDF() {
//     if (!this.report()) return;

//     const pdfMake = await this.loadPdfMake();
//     const data = this.report()!;

//     const sentiment = this.getOverallSentiment(data);

//     const docDefinition: TDocumentDefinitions = {
//       pageSize: 'A4',
//       pageMargins: [40, 60, 40, 60],
//       defaultStyle: {
//         font: 'Inter', // Use your Inter font
//         fontSize: 12,
//         color: '#000000',
//       },

//       content: [
//         // Centered header stack
//         {
//           stack: [
//             { text: data.ticker.toUpperCase(), style: 'ticker', alignment: 'center' },
//             { text: sentiment, style: 'sentiment', alignment: 'center' },
//             { text: 'Equity Research Report', style: 'subheader', alignment: 'center' },
//           ],
//           margin: [0, 0, 0, 40],
//         },

//         { text: 'Overall Conclusion', style: 'sectionHeader' },
//         ...this.mdToContent(data.combined_sentiment),

//         { text: '', pageBreak: 'after', margin: [0, 20, 0, 0] },

//         // Full-width sections
//         { text: 'Fundamental', style: 'cardHeader' },
//         ...this.mdToContent(data.sentiment_analysis.fundamental),

//         { text: 'Technical', style: 'cardHeader', margin: [0, 20, 0, 8] },
//         ...this.mdToContent(data.sentiment_analysis.technical),

//         { text: 'Peer Comparison', style: 'cardHeader', margin: [0, 20, 0, 8] },
//         ...this.mdToContent(data.sentiment_analysis.peer),

//         { text: 'Industry', style: 'cardHeader', margin: [0, 20, 0, 8] },
//         ...this.mdToContent(data.sentiment_analysis.industry),

//         { text: 'News & Sentiment', style: 'cardHeader', margin: [0, 20, 0, 8] },
//         ...this.mdToContent(data.sentiment_analysis.news),

//         { text: 'Macro Factors', style: 'cardHeader', margin: [0, 20, 0, 8] },
//         ...this.mdToContent(data.sentiment_analysis.macro),
//       ],

//       styles: {
//         ticker: { fontSize: 36, bold: true, color: '#000000' },
//         sentiment: { fontSize: 20, bold: true, color: '#000000', padding: 8 }, // Black, no background
//         subheader: { fontSize: 18, italics: true, color: '#000000', margin: [0, 10, 0, 0] },
//         sectionHeader: { fontSize: 24, bold: true, color: '#000000', margin: [0, 20, 0, 10] },
//         cardHeader: { fontSize: 18, bold: true, color: '#000000', margin: [0, 20, 0, 8] },
//         header: { fontSize: 16, bold: true, color: '#000000' }, // For inline # headings if any
//       } as StyleDictionary,
//     };

//     const pdfDocGenerator = pdfMake.createPdf(docDefinition);
//     pdfDocGenerator.getBlob((blob: Blob) => {
//       const url = URL.createObjectURL(blob);
//       window.open(url, '_blank');
//       setTimeout(() => URL.revokeObjectURL(url), 10000);
//     });
//   }
// }
