// src/app/shared/simple-markdown/simple-markdown.component.ts
import { Component, Input } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-simple-markdown',
  standalone: true,
  imports: [CommonModule],
  template: `<div
    class="prose prose-invert max-w-none"
    [innerHTML]="rendered"
  ></div>`,
  styles: `
    :host ::ng-deep {
      h1 { @apply text-3xl font-black text-lime-400 mt-10 mb-6; }
      h2 { @apply text-2xl font-bold text-lime-400 mt-10 mb-5; }
      h3 { @apply text-xl font-bold text-lime-300 mt-8 mb-4; }
      strong, b { @apply text-lime-300 font-bold; }
      ul, ol { @apply my-5 pl-7 space-y-2; }
      li { @apply leading-relaxed; }
      code { @apply bg-gray-800 text-lime-300 px-1.5 py-0.5 rounded text-sm; }
      pre { @apply bg-gray-900/80 p-5 rounded-xl overflow-x-auto border border-white/10 my-8; }
      blockquote { @apply border-l-4 border-lime-400 pl-6 italic bg-white/5 py-4 my-8 rounded-r-xl; }
      hr { @apply border-white/10 my-10; }
      a { @apply text-lime-400 underline hover:text-lime-300; }
    }
  `,
})
export class SimpleMarkdownComponent {
  private _markdown = '';
  rendered: SafeHtml = '';

  @Input({ required: true })
  set markdown(value: string) {
    if (value !== this._markdown) {
      this._markdown = value ?? '';
      this.rendered = this.sanitizer.bypassSecurityTrustHtml(
        this.toHtml(this._markdown)
      );
    }
  }

  constructor(private sanitizer: DomSanitizer) {}

  private toHtml(md: string): string {
    if (!md) return '';

    let html = md
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/__(.*)__/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/_(.*)_/gim, '<em>$1</em>')
      .replace(/^\s*[-*+] (.*$)/gim, '<ul><li>$1</li></ul>')
      .replace(/^\s*\d+\. (.*$)/gim, '<ol><li>$1</li></ol>')
      .replace(/```([\s\S]*?)```/gim, '<pre><code>$1</code></pre>')
      .replace(/`(.*?)`/gim, '<code>$1</code>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\n/gim, '<br>');

    // Fix list tags
    html = html.replace(/<\/ul><ul>/g, '').replace(/<\/ol><ol>/g, '');
    return html;
  }
}