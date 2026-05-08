import React, { useEffect } from "react";
import { useHistory, useLocation } from "@docusaurus/router";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

/**
 * 首页统一重定向到中文 RDK 文档首页。
 * 解决语言检测命中 /en/ 时未进入中文首页的问题。
 */
export default function HomeRedirect() {
  const history = useHistory();
  const location = useLocation();
  const { siteConfig } = useDocusaurusContext();

  useEffect(() => {
    history.replace(`${siteConfig.baseUrl}RDK${location.search}${location.hash}`);
  }, [history, location.search, location.hash, siteConfig.baseUrl]);

  return null;
}
