import React, { createContext, useCallback, useContext, useMemo } from 'react';
import { useHistory, useLocation } from '@docusaurus/router';
import { PRODUCT_VERSION_MATRIX, VERSION_PRODUCT_MATRIX } from './doc-scope-matrix.js';
import {
  resolveCanonicalProductKeyForMatrix,
  resolveProductForVersion,
} from './doc-scope-product-utils.js';

export { PRODUCT_VERSION_MATRIX, VERSION_PRODUCT_MATRIX } from './doc-scope-matrix.js';

const DEFAULT_VERSION = '3.0.0';
const DEFAULT_PRODUCT = VERSION_PRODUCT_MATRIX[DEFAULT_VERSION][0];

const STORAGE_KEY_VERSION = 'doc_scope_version';
const STORAGE_KEY_PRODUCT = 'doc_scope_product';

const defaultCtx = {
  version: DEFAULT_VERSION,
  product: DEFAULT_PRODUCT,
  setVersion: () => {},
  setProduct: () => {},
  matrix: VERSION_PRODUCT_MATRIX,
};

export const DocScopeFilterContext = createContext(defaultCtx);

export function useDocScopeFilter() {
  return useContext(DocScopeFilterContext);
}

function normalizeVersionFromQuery(v) {
  if (v && VERSION_PRODUCT_MATRIX[v]) {
    return v;
  }
  return DEFAULT_VERSION;
}

function saveToStorage(version, product) {
  try {
    localStorage.setItem(STORAGE_KEY_VERSION, version);
    localStorage.setItem(STORAGE_KEY_PRODUCT, product);
  } catch (e) {
    // localStorage 不可用时忽略
  }
}

function loadFromStorage() {
  try {
    const v = localStorage.getItem(STORAGE_KEY_VERSION);
    const pRaw = localStorage.getItem(STORAGE_KEY_PRODUCT);
    if (v && VERSION_PRODUCT_MATRIX[v]) {
      const p = resolveProductForVersion(pRaw, v);
      return { version: v, product: p };
    }
  } catch (e) {
    // localStorage 不可用时忽略
  }
  return null;
}

/**
 * 从 URL 查询参数解析版本和产品，如果没有则从 localStorage 读取，最后使用默认值。
 */
function parseFilter(search) {
  const normalized = !search
    ? ''
    : search.startsWith('?')
      ? search.slice(1)
      : search;
  const q = new URLSearchParams(normalized);
  if (q.get('v')) {
    const v = normalizeVersionFromQuery(q.get('v'));
    const list = VERSION_PRODUCT_MATRIX[v];
    const pRaw = q.get('p');
    const p = resolveProductForVersion(pRaw, v);
    return { version: v, product: p };
  }
  const stored = loadFromStorage();
  if (stored) {
    return stored;
  }
  return { version: DEFAULT_VERSION, product: DEFAULT_PRODUCT };
}

function replaceSearch(history, location, nextSearch) {
  const search = nextSearch && nextSearch.length ? (nextSearch.startsWith('?') ? nextSearch : `?${nextSearch}`) : '';
  if (location.search === search) {
    return;
  }
  history.replace({
    pathname: location.pathname,
    search,
    hash: location.hash,
    state: location.state,
  });
}

export function DocScopeFilterProvider({ children }) {
  const location = useLocation();
  const history = useHistory();

  const { version, product } = useMemo(
    () => parseFilter(location.search),
    [location.search],
  );

  useMemo(() => {
    saveToStorage(version, product);
  }, [version, product]);

  const setVersion = useCallback(
    (v) => {
      const newV = normalizeVersionFromQuery(v);
      const list = VERSION_PRODUCT_MATRIX[newV] || VERSION_PRODUCT_MATRIX[DEFAULT_VERSION];
      const nextP = list[0];
      const next = new URLSearchParams(location.search);
      next.set('v', newV);
      next.set('p', nextP);
      replaceSearch(history, location, `?${next.toString()}`);
    },
    [location, history],
  );

  const setProduct = useCallback(
    (p) => {
      const canonical = resolveCanonicalProductKeyForMatrix(p);
      if (!canonical) {
        return;
      }
      const versions = PRODUCT_VERSION_MATRIX[canonical];
      if (!versions || versions.length === 0) {
        return;
      }
      const nextV = versions[0];
      const next = new URLSearchParams(location.search);
      next.set('v', nextV);
      next.set('p', canonical);
      replaceSearch(history, location, `?${next.toString()}`);
    },
    [location, history],
  );

  const value = useMemo(
    () => ({
      version,
      product,
      setVersion,
      setProduct,
      matrix: VERSION_PRODUCT_MATRIX,
      productMatrix: PRODUCT_VERSION_MATRIX,
    }),
    [version, product, setVersion, setProduct],
  );

  return <DocScopeFilterContext.Provider value={value}>{children}</DocScopeFilterContext.Provider>;
}
