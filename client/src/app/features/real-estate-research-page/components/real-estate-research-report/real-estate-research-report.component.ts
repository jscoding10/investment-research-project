import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';

import { MarkdownModule } from 'ngx-markdown';
import { TooltipModule } from 'primeng/tooltip';

import { unified } from 'unified';
import remarkGfm from 'remark-gfm';
import remarkParse from 'remark-parse';

import type { Content, StyleDictionary, TDocumentDefinitions } from 'pdfmake/interfaces';

import { RealEstateReport } from '../../types';

import { RealEstateResearchStateService } from '../../services/real-estate-research-state.service';

@Component({
  selector: 'app-real-estate-research-report',
  imports: [CommonModule, MarkdownModule, TooltipModule],
  templateUrl: './real-estate-research-report.component.html',
  styleUrl: './real-estate-research-report.component.css',
})
export class RealEstateResearchReportComponent {
  private state = inject(RealEstateResearchStateService);

  report = this.state.report;
  isLoading = this.state.isLoading;
  address = this.state.address;
  error = this.state.error;

  private pdfMakeInstance: any = null;

  private parser: any = null;

  private getParser() {
    if (!this.parser) {
      this.parser = unified().use(remarkParse).use(remarkGfm);
    }
    return this.parser;
  }

  getOverallRecommendation(report: RealEstateReport): 'STRONG BUY' | 'HOLD' | 'AVOID' | 'NEUTRAL' {
    if (!report?.combined_analysis) return 'NEUTRAL';

    const text = report.combined_analysis.toUpperCase();

    if (
      text.includes('STRONG BUY') ||
      text.includes('OVERALL RECOMMENDATION: STRONG BUY') ||
      text.includes('**OVERALL RECOMMENDATION:** STRONG BUY') ||
      text.includes('STRONG BUY RECOMMENDATION')
    ) {
      return 'STRONG BUY';
    }

    if (
      text.includes('OVERALL RECOMMENDATION: HOLD') ||
      text.includes('**OVERALL RECOMMENDATION:** HOLD') ||
      text.includes('HOLD')
    ) {
      return 'HOLD';
    }

    if (
      text.includes('OVERALL RECOMMENDATION: AVOID') ||
      text.includes('**OVERALL RECOMMENDATION:** AVOID') ||
      text.includes('AVOID')
    ) {
      return 'AVOID';
    }

    return 'NEUTRAL';
  }

  private normalizeMarkdown(md: string): string {
    if (!md) return '';
    return md
      .replace(/\u202F/g, ' ')
      .replace(/\u2011/g, '-')
      .replace(/[\u2013\u2014]/g, '-')
      .replace(/[\u201C\u201D]/g, '"')
      .replace(/[\u2018\u2019]/g, "'")
      .replace(/\u2248/g, '~')
      .replace(/\b([A-Z]{1,6})\/([A-Z]{1,6})\b/gi, '$1\u2044$2')
      .replace(/[ \t]+/g, ' ')
      .trim();
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
            if (child.type === 'text') paragraphContent.push(child.value);
            else if (child.type === 'strong')
              paragraphContent.push({ text: child.children[0]?.value || '', bold: true });
            else if (child.type === 'emphasis')
              paragraphContent.push({ text: child.children[0]?.value || '', italics: true });
          });
          return paragraphContent.length > 0
            ? { text: paragraphContent, margin: [0, 8, 0, 8], alignment: 'justify' }
            : undefined;
        }

        case 'heading': {
          const level = node.depth;
          const text = node.children.map((c: any) => c.value || '').join('');
          const fontSize = level === 1 ? 20 : level === 2 ? 18 : 16;
          return text
            ? { text, style: 'sectionHeader', fontSize, margin: [0, 30, 0, 12], alignment: 'left' }
            : undefined;
        }

        case 'list': {
          const items: Content[] = [];
          node.children.forEach((item: any) => {
            const listItemContent: (string | { text: string; bold?: true; italics?: true })[] = [];
            if (item.children.length > 0) {
              item.children.forEach((child: any) => {
                if (child.type === 'paragraph') {
                  child.children.forEach((grachi: any) => {
                    if (grachi.type === 'text') listItemContent.push(grachi.value);
                    else if (grachi.type === 'strong')
                      listItemContent.push({ text: grachi.children[0]?.value || '', bold: true });
                    else if (grachi.type === 'emphasis')
                      listItemContent.push({ text: grachi.children[0]?.value || '', italics: true });
                  });
                }
              });
            }
            items.push(listItemContent.length > 0 ? { text: listItemContent } : { text: '•' });
          });
          return { [node.ordered ? 'ol' : 'ul']: items, margin: [20, 6, 0, 10] } as unknown as Content;
        }

        default:
          return node.value ? { text: node.value, margin: [0, 8, 0, 8] } : undefined;
      }
    };

    return tree.children.flatMap(visit).filter(Boolean) as Content[];
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

    const rec = this.getOverallRecommendation(data);

    const docDefinition: TDocumentDefinitions = {
      pageSize: 'A4',
      pageMargins: [40, 60, 40, 60],
      defaultStyle: { font: 'Inter', fontSize: 12, color: '#000000' },

      content: [
        { text: `${data.address} Real Estate Research Report`, style: 'ticker', margin: [0, 0, 0, 10] },
        {
          text: `Recommendation: ${rec}`,
          style: 'recommendation',
          margin: [0, 0, 0, 20],
        },
        ...this.mdToContent(data.combined_analysis),
        { text: '', pageBreak: 'after' },

        { text: 'Market Trends', style: 'sectionHeader' },
        { stack: this.mdToContent(data.analysis.market), style: 'sentimentText' },

        { text: 'Financial Analysis', style: 'sectionHeader' },
        { stack: this.mdToContent(data.analysis.financial), style: 'sentimentText' },

        { text: 'Risk Assessment', style: 'sectionHeader' },
        { stack: this.mdToContent(data.analysis.risk), style: 'sentimentText' },
      ],

      styles: {
        ticker: { fontSize: 18, bold: true, color: '#000000' },
        recommendation: { fontSize: 16, bold: true, color: '#000000', alignment: 'center' },
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
