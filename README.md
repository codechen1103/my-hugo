# 我的 Hugo 博客

这是一个使用 Hugo 构建的个人博客，支持从 Obsidian 私有仓库自动同步文章。

## ✨ 特性

- 🚀 使用 Hugo 静态网站生成器
- 🎨 使用 Ananke 主题
- 🔄 自动从 Obsidian 仓库同步文章
- 📝 支持 Markdown 写作
- 🌐 支持中文

## 📦 项目结构

```
.
├── .github/
│   ├── workflows/
│   │   └── sync-obsidian.yml      # GitHub Actions 自动同步配置
│   └── scripts/
│       └── sync-posts.py          # 文章同步脚本
├── content/
│   └── posts/                     # 博客文章目录
├── docs/
│   └── OBSIDIAN_SYNC_SETUP.md     # Obsidian 同步配置文档
├── themes/
│   └── ananke/                    # Hugo 主题
└── hugo.toml                      # Hugo 配置文件
```

## 🚀 快速开始

### 本地开发

1. 安装 Hugo：
   ```bash
   # Windows (使用 Chocolatey)
   choco install hugo-extended
   
   # macOS (使用 Homebrew)
   brew install hugo
   
   # Linux (使用包管理器)
   sudo apt-get install hugo
   ```

2. 克隆仓库：
   ```bash
   git clone <your-repo-url>
   cd my-hugo
   ```

3. 启动本地服务器：
   ```bash
   hugo server -D
   ```

4. 访问 http://localhost:1313 查看博客

### 创建新文章

```bash
hugo new posts/my-new-post.md
```

## 🔄 Obsidian 自动同步

本博客支持从私有 Obsidian 仓库自动同步文章。只需在 Obsidian 笔记的 front matter 中添加 `share: true`，文章就会自动同步到博客。

### 配置步骤

详细配置步骤请参考：[Obsidian 同步配置文档](docs/OBSIDIAN_SYNC_SETUP.md)

### 快速配置

1. 创建 GitHub Personal Access Token
2. 在博客仓库中配置 Secrets：
   - `OBSIDIAN_REPO`: 你的 Obsidian 仓库名（格式：`username/repo-name`）
   - `OBSIDIAN_TOKEN`: 你的 Personal Access Token
3. 在 Obsidian 笔记中添加 `share: true` 属性

### 同步示例

在 Obsidian 中创建笔记：

```markdown
---
title: 我的技术文章
date: 2025-12-28
share: true
tags:
  - 技术
  - 教程
---

这是文章内容...
```

该文章会自动同步到博客的 `content/posts/` 目录。

## 📝 写作指南

### Front Matter 格式

支持 YAML 和 TOML 两种格式：

**YAML 格式：**
```yaml
---
title: 文章标题
date: 2025-12-28
draft: false
tags:
  - 标签1
  - 标签2
---
```

**TOML 格式：**
```toml
+++
title = '文章标题'
date = '2025-12-28T10:00:00+08:00'
draft = false
tags = ['标签1', '标签2']
+++
```

## 🛠️ 构建和部署

### 本地构建

```bash
hugo
```

构建后的静态文件会生成在 `public/` 目录。

### 部署到 GitHub Pages

1. 在仓库设置中启用 GitHub Pages
2. 选择 `gh-pages` 分支作为源
3. 推送代码后会自动构建和部署

### 部署到其他平台

- **Netlify**: 连接 GitHub 仓库，设置构建命令为 `hugo`
- **Vercel**: 导入项目，选择 Hugo 框架
- **Cloudflare Pages**: 连接仓库，构建命令 `hugo`

## 📚 相关文档

- [Hugo 官方文档](https://gohugo.io/documentation/)
- [Ananke 主题文档](https://github.com/theNewDynamic/gohugo-theme-ananke)
- [Obsidian 同步配置](docs/OBSIDIAN_SYNC_SETUP.md)

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！