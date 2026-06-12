/**
 * 监听文件变化，自动重新生成侧边栏配置文件
 * 用于开发环境，当修改 _sidebar_scope.json 或 Markdown 的 Front Matter 时自动更新配置。
 * 监听范围：docs/、i18n/en/docusaurus-plugin-content-docs/current/（若存在）。
 */
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const {
  getGeneratedSidebarConfigPath,
} = require('./lib/sidebar-scope-config-generator');

const docsDir = path.join(__dirname, '../docs');
const i18nEnDocsCurrentDir = path.join(
  __dirname,
  '../i18n/en/docusaurus-plugin-content-docs/current',
);
const configFilePath = getGeneratedSidebarConfigPath(path.join(__dirname, '..'));

let isGenerating = false;
let lastGenerateTime = 0;

/**
 * 重新生成配置文件
 */
function regenerateConfig() {
  // 防抖：如果距离上次生成不到 1 秒，则跳过
  const now = Date.now();
  if (now - lastGenerateTime < 1000) {
    return;
  }
  
  // 如果正在生成，则跳过
  if (isGenerating) {
    return;
  }
  
  isGenerating = true;
  lastGenerateTime = now;
  
  console.log('\nDetected file changes. Regenerating config...\n');
  
  // 禁用 shell：项目路径含空格时（如 rdk x5），shell: true 会把路径截断，导致 MODULE_NOT_FOUND
  const scriptPath = path.join(__dirname, 'generate-sidebar-config.js');
  const generate = spawn(process.execPath, [scriptPath], {
    stdio: 'inherit',
    shell: false,
    cwd: path.join(__dirname, '..'),
  });
  
  generate.on('close', (code) => {
    isGenerating = false;
    if (code === 0) {
      console.log('\nConfig file updated.\n');
    } else {
      console.log('\nConfig generation failed.\n');
    }
  });
}

/**
 * 监听目录变化
 */
function watchDirectory(dir) {
  if (!fs.existsSync(dir)) {
    return;
  }
  
  fs.watch(dir, { recursive: true }, (eventType, filename) => {
    if (!filename) {
      return;
    }
    
    // 只监听特定文件
    if (filename.endsWith('_sidebar_scope.json') || 
        (filename.endsWith('.md') && !filename.includes('node_modules'))) {
      console.log(`File changed: ${filename}`);
      regenerateConfig();
    }
  });
  
  console.log(`Watching directory: ${dir}`);
}

/**
 * 主函数
 */
function main() {
  console.log('Starting config file watcher...\n');
  
  // 监听 docs 目录
  watchDirectory(docsDir);

  // 监听英文 i18n 当前文档目录
  if (fs.existsSync(i18nEnDocsCurrentDir)) {
    watchDirectory(i18nEnDocsCurrentDir);
  }
  
  console.log(
    '\nWatcher started. Updating _sidebar_scope.json or Markdown front matter (including i18n/en/.../current) will auto-regenerate the config file.\n',
  );
  console.log('Press Ctrl+C to stop watching.\n');
}

main();
