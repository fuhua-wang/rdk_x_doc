import React, { useEffect } from "react";
import docsearch from "@docsearch/js";
import "@docsearch/css";

export default function SearchBar() {
  useEffect(() => {
    const instance = docsearch({
      container: "#docsearch",
      appId: "H4A6YGWITH",
      indexName: "rdk_doc_crawler",
      apiKey: "c092d1c639012a44ebe542dfa25e1635",
      // askAi: "YOUR_ALGOLIA_ASSISTANT_ID", // TODO: Replace with your Algolia Assistant ID
    });

    return () => {
      if (instance && typeof instance.destroy === "function") {
        instance.destroy();
      }
    };
  }, []);

  return <div id="docsearch" />;
}
