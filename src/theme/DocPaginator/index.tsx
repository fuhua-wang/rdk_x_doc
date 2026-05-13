import React from 'react';
import DocPaginator from '@theme-original/DocPaginator';
import {useLocation} from '@docusaurus/router';
import type {Props} from '@theme/DocPaginator';

function containsChinese(text: string): boolean {
  return /[\u4e00-\u9fff]/.test(text);
}

function titleCaseWord(word: string): string {
  const lower = word.toLowerCase();
  const acronymMap: Record<string, string> = {
    faq: 'FAQs',
    os: 'OS',
    sdk: 'SDK',
    api: 'API',
    bpu: 'BPU',
    cpu: 'CPU',
    gpu: 'GPU',
    ros: 'ROS',
    tros: 'TROS',
    rdk: 'RDK',
    i2c: 'I2C',
    spi: 'SPI',
    uart: 'UART',
    gpio: 'GPIO',
  };
  if (acronymMap[lower]) {
    return acronymMap[lower];
  }
  if (/^x\d+$/i.test(word)) {
    return word.toUpperCase();
  }
  return lower.charAt(0).toUpperCase() + lower.slice(1);
}

function deriveEnglishTitleFromPermalink(permalink: string): string | null {
  const cleanPath = String(permalink || '')
    .split('#')[0]
    .split('?')[0]
    .replace(/\/+$/, '');
  if (!cleanPath) return null;

  const segments = cleanPath.split('/').filter(Boolean);
  if (segments.length === 0) return null;

  let slug = segments[segments.length - 1];
  if (slug === 'en' && segments.length > 1) {
    slug = segments[segments.length - 2];
  }

  slug = decodeURIComponent(slug)
    .replace(/\.(md|mdx|html)$/i, '')
    .replace(/^\d+(?:[_-]\d+)*[_-]+/, '')
    .trim();

  if (!slug) return null;

  const words = slug
    .replace(/[_-]+/g, ' ')
    .split(/\s+/)
    .filter(Boolean)
    .map(titleCaseWord);

  if (words.length === 0) return null;
  return words.join(' ');
}

function extractNumberPrefix(title: string): string | null {
  const numbered = String(title || '').trim().match(/^(\d+(?:\.\d+)*)\s*[. ]\s*/);
  return numbered?.[1] ?? null;
}

function looksLikeUnderscoreCodeTitle(title: string): boolean {
  return /(?:^|\s)\d+_\d+_|[A-Za-z]_[A-Za-z]/.test(title);
}

function normalizePaginatorTitle(
  title: string | undefined,
  permalink: string,
  locale: string,
): string | undefined {
  if (!title) return title;
  if (locale !== 'en') {
    return title;
  }

  const problematic = containsChinese(title) || looksLikeUnderscoreCodeTitle(title);
  if (!problematic) {
    return title;
  }

  const derived = deriveEnglishTitleFromPermalink(permalink);
  if (!derived) {
    return title;
  }

  const numberPrefix = extractNumberPrefix(title);
  if (numberPrefix) {
    return `${numberPrefix}. ${derived}`;
  }
  return derived;
}

export default function DocPaginatorWrapper(props: Props): JSX.Element {
  const { pathname } = useLocation();
  const { previous, next } = props;
  
  const getCurrentLocale = () => {
    if (pathname.includes('/en/')) return 'en';
    return 'zh';
  };
  
  const currentLocale = getCurrentLocale();
  
  const customNext = next ? {
    ...next,
    title: normalizePaginatorTitle(next.title, next.permalink, currentLocale),
  } : null;

  const customPrevious = previous ? {
    ...previous,
    title: normalizePaginatorTitle(previous.title, previous.permalink, currentLocale),
  } : null;

  return (
    <DocPaginator
      previous={customPrevious}
      next={customNext}
    />
  );
}