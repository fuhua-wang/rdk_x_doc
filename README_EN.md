# RDK DOC

English | [简体中文](./README.md)

A Docusaurus-based multilingual documentation site for RDK, supporting multi-dimensional content filtering (version × product).

## Features

- 📝 **Multilingual Support**: Chinese (zh-Hans) and English (en) language switching
- 🔧 **Multi-dimensional Filtering**: Dynamically display content based on version and product
- 🔍 **Search**: Pagefind with isolated indexes per product/version scope
- 📊 **Mermaid Diagrams**: Support for Mermaid flowcharts and diagrams
- 💬 **Giscus Comments**: Integrated Giscus comment system
- 👀 **File Watching**: Auto-update configuration when files change during development
- 🚀 **GitHub Pages**: Support for GitHub Pages deployment

### Search Build

- `npm run build:pagefind:matrix` builds each product/version scope and generates a dedicated Pagefind index.
- Example output layout: `build/RDK_X5/3.5.0/pagefind/`.
- `npm run build:rdk-studio-index` crawls and generates a local RDK Studio federation index at `static/rdk_studio_search_index.json`.
- `npm run start` is for development server only (it does not build Pagefind indexes).
- To test search, run `npm run prepare-pagefind-dev` (dev indexes) or `npm run build:pagefind:matrix` (full matrix indexes) first.
- Dev index preparation uses `core` mode by default (builds `RDK X3@3.0.0` and `RDK X5@3.5.0`). Use `DOC_PAGEFIND_DEV_MODE=full` to build the full matrix.

## Quick Start

### Requirements

- Node.js >= 18.0

### Install Dependencies

```bash
npm install
```

### Development Mode

Start Chinese documentation (with file watching):
```bash
npm run start
```
Access URL: http://localhost:3000/rdk_x_doc/

Start English documentation (with file watching):
```bash
npm run start:en
```
Access URL: http://localhost:3000/rdk_x_doc/en/

Start Chinese documentation (without file watching):
```bash
npm run start:no-watch
```
Access URL: http://localhost:3000/rdk_x_doc/

Start English documentation (without file watching):
```bash
npm run start:no-watch:en
```
Access URL: http://localhost:3000/rdk_x_doc/en/

Start with specific port:
```bash
npm run start:port
```
Access URL: http://localhost:3001/rdk_x_doc/

## Build & Deploy

### Build Production Version

```bash
npm run build
```

### Preview Build Result Locally

```bash
npm run serve
```

Access URLs:
- Chinese documentation: http://localhost:3000/rdk_x_doc/
- English documentation: http://localhost:3000/rdk_x_doc/en/

### Deploy to GitHub Pages

```bash
npm run deploy
```

## Project Structure

```
.
├── docs/                 # Documentation directory
├── i18n/                 # Multilingual translation files
├── scripts/              # Script files
│   ├── generate-sidebar-config.js   # Generate sidebar configuration
│   └── watch-sidebar-config.js     # Watch file changes
├── src/
│   ├── components/       # React components
│   ├── context/          # Context state management
│   ├── pages/            # Page components
│   ├── remark/           # Remark plugins
│   └── theme/            # Docusaurus theme components
├── static/               # Static resources
├── docusaurus.config.js  # Docusaurus configuration
├── sidebars.js           # Sidebar configuration
└── package.json
```

## Core Features

### Multi-dimensional Content Filtering

Configure document visibility for specific versions and products via Front Matter:

```markdown
---
sidebar_versions: ">= 3.5.0"
sidebar_products: "RDK X5"
---
```

Or create `_sidebar_scope.json` in folders:

```json
{
  "sidebar_versions": ">= 3.5.0",
  "sidebar_products": "RDK X5"
}
```

### DocScope Component

Control content display using `:::doc_scope` directive:

```markdown
:::doc_scope versions="3.0.0" products="RDK X3"
This content only shows under RDK X3 3.0.0
:::
```

## Common Commands

| Command | Description |
|---------|-------------|
| `npm run generate-sidebar-config` | Manually generate sidebar config |
| `npm run clear` | Clear Docusaurus cache |
| `npm run swizzle` | Customize theme components |
| `npm run write-translations` | Extract translation content |

## Tech Stack

- **Docusaurus**: 3.7.0
- **React**: 18.x
- **Remark**: Markdown parsing plugins
- **Rehype**: HTML processing plugins
- **Mermaid**: Diagram rendering
- **Giscus**: Comment system

