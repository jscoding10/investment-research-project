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
import { CryptoReport } from '../../services/crypto-research-state.service';
import { CryptoResearchStateService } from '../../services/crypto-research-state.service';

@Component({
  selector: 'app-crypto-research-report',
  imports: [CommonModule, MarkdownModule, TooltipModule],
  templateUrl: './crypto-research-report.component.html',
  styleUrl: './crypto-research-report.component.css',
})
export class CryptoResearchReportComponent {
  private state = inject(CryptoResearchStateService);

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

  getOverallReport(report: CryptoReport | null): string {
    if (!report) return 'NEUTRAL';
    const match = report.combined_sentiment.match(/Overall Sentiment: (\w+)/);
    return match ? (match[1] as 'BULLISH' | 'BEARISH' | 'NEUTRAL') : 'NO REPORT';
  }

  getOverallSentiment(report: CryptoReport): 'BULLISH' | 'BEARISH' | 'NEUTRAL' {
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
          return undefined;
        }

        case 'heading': {
          const level = node.depth;
          const text = node.children.map((c: any) => c.value || '').join('');
          const fontSize = level === 1 ? 20 : level === 2 ? 18 : 16;

          if (text) {
            return {
              text,
              style: 'sectionHeader',
              fontSize,
              margin: [0, 30, 0, 12],
              alignment: 'left',
            };
          }
          return undefined;
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
          return undefined;
      }
    };

    const result = tree.children.flatMap(visit).filter(Boolean) as Content[];
    return result;
  }

  private async loadPdfMake() {
    if (!this.pdfMakeInstance) {
      const pdfMakeLib = await import('pdfmake/build/pdfmake');
      this.pdfMakeInstance = pdfMakeLib.default;

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

  async exportToPDF() {
    if (!this.report()) return;

    const pdfMake = await this.loadPdfMake();
    const data = this.report()!;

    const sentiment = this.getOverallSentiment(data);

    const docDefinition: TDocumentDefinitions = {
      pageSize: 'A4',
      pageMargins: [40, 60, 40, 60],
      defaultStyle: {
        font: 'Inter',
        fontSize: 12,
        color: '#000000',
      },

      content: [
        {
          stack: [
            {
              text: `${data.ticker.toUpperCase()} Crypto Research Report`,
              style: 'ticker',
            },
          ],
          margin: [0, 0, 0, 10],
        },

        ...this.mdToContent(data.combined_sentiment),

        { text: '', pageBreak: 'after', margin: [0, 0, 0, 0] },

        { text: 'Technical', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.technical), style: 'sentimentText' },

        { text: 'Peer Comparison', style: 'sectionHeader' },
        { stack: this.mdToContent(data.sentiment_analysis.peer), style: 'sentimentText' },

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
