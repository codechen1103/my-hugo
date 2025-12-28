# Obsidian 文章自动同步配置指南

本文档说明如何配置 GitHub Actions 以实现从私有 Obsidian 仓库自动同步文章到公开的 Hugo 博客仓库。

## 📋 功能特性

- ✅ 自动同步带有 `share: true` 属性的 Markdown 文章
- ✅ 支持定时同步（每天凌晨 2 点）
- ✅ 支持手动触发同步
- ✅ 自动转换 front matter 格式为 Hugo 兼容格式
- ✅ 保留文章的目录结构
- ✅ 自动提交更改到博客仓库

## 🔧 配置步骤

### 1. 创建 Personal Access Token (PAT)

需要创建一个有权限访问私有 Obsidian 仓库的 GitHub Token：

1. 访问 GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 设置 Token 名称，如 `obsidian-sync-token`
4. 选择过期时间（建议选择 "No expiration" 或较长时间）
5. 勾选以下权限：
   - `repo` (完整的仓库访问权限)
6. 点击 "Generate token" 并**立即复制保存** Token（只会显示一次）

### 2. 配置 GitHub Secrets

在**博客仓库**（公开仓库）中配置以下 Secrets：

1. 进入博客仓库的 Settings → Secrets and variables → Actions
2. 点击 "New repository secret" 添加以下 Secrets：

#### OBSIDIAN_REPO
- **名称**: `OBSIDIAN_REPO`
- **值**: 你的 Obsidian 私有仓库名称，格式为 `username/repo-name`
- **示例**: `yourusername/obsidian-vault`

#### OBSIDIAN_TOKEN
- **名称**: `OBSIDIAN_TOKEN`
- **值**: 在步骤 1 中创建的 Personal Access Token
- **示例**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 3. 在 Obsidian 中标记要分享的文章

在你的 Obsidian 笔记的 front matter 中添加 `share: true` 属性：

#### YAML 格式示例：
```markdown
---
title: 我的文章标题
date: 2025-12-28
share: true
tags:
  - 技术
  - 博客
---

文章内容...
```

#### TOML 格式示例：
```markdown
+++
title = '我的文章标题'
date = '2025-12-28T10:00:00+08:00'
share = true
tags = ['技术', '博客']
+++

文章内容...
```

**注意**：
- 只有包含 `share: true` 的文章才会被同步
- `share` 字段支持多种格式：`true`, `"true"`, `yes`, `1`
- 同步后的文章会自动移除 `share` 字段

## 🚀 使用方法

### 自动同步

配置完成后，GitHub Actions 会在以下情况自动运行：

1. **定时触发**：每天北京时间凌晨 2:00 自动同步
2. **工作流更新**：当 [`sync-obsidian.yml`](.github/workflows/sync-obsidian.yml:1) 文件被修改时

### 手动同步

如果需要立即同步文章：

1. 进入博客仓库的 Actions 页面
2. 选择 "同步 Obsidian 文章" workflow
3. 点击 "Run workflow" 按钮
4. 选择分支（通常是 `main`）
5. 点击绿色的 "Run workflow" 按钮

## 📁 文件结构

同步后的文件结构：

```
博客仓库/
├── .github/
│   ├── workflows/
│   │   └── sync-obsidian.yml          # GitHub Actions 工作流配置
│   └── scripts/
│       └── sync-posts.py              # Python 同步脚本
├── content/
│   └── posts/                         # 同步的文章会保存在这里
│       ├── article1.md
│       └── subfolder/
│           └── article2.md
└── docs/
    └── OBSIDIAN_SYNC_SETUP.md         # 本配置文档
```

## 🔍 工作流程说明

1. **检出仓库**：检出博客仓库和 Obsidian 仓库
2. **设置环境**：安装 Python 和必要的依赖（PyYAML）
3. **执行同步**：运行 [`sync-posts.py`](.github/scripts/sync-posts.py:1) 脚本
   - 扫描 Obsidian 仓库中的所有 Markdown 文件
   - 检查 front matter 中的 `share` 字段
   - 转换格式并复制到博客仓库的 `content/posts/` 目录
4. **提交更改**：如果有新文章或更新，自动提交到博客仓库
5. **完成通知**：输出同步统计信息

## 🎨 自定义配置

### 修改同步时间

编辑 [`.github/workflows/sync-obsidian.yml`](.github/workflows/sync-obsidian.yml:9) 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 18 * * *'  # UTC 18:00 = 北京时间 02:00
```

常用时间示例：
- 每天凌晨 2:00：`'0 18 * * *'`
- 每天中午 12:00：`'0 4 * * *'`
- 每 6 小时一次：`'0 */6 * * *'`

### 修改 Obsidian 文章路径

如果你的 Obsidian 文章不在仓库根目录，可以修改 [`sync-posts.py`](.github/scripts/sync-posts.py:14) 中的路径：

```python
OBSIDIAN_POSTS_PATH = OBSIDIAN_VAULT_PATH / "posts"  # 例如：只同步 posts 目录
```

### 修改目标路径

如果想将文章同步到不同的目录，修改：

```python
HUGO_CONTENT_PATH = Path("content/blog")  # 改为其他目录
```

## 🐛 故障排查

### 同步失败

1. **检查 Secrets 配置**
   - 确认 `OBSIDIAN_REPO` 格式正确（`username/repo-name`）
   - 确认 `OBSIDIAN_TOKEN` 有效且有足够权限

2. **检查 Token 权限**
   - Token 必须有 `repo` 权限
   - Token 未过期

3. **查看 Actions 日志**
   - 进入 Actions 页面查看详细错误信息
   - 检查 Python 脚本的输出

### 文章未同步

1. **检查 front matter**
   - 确认包含 `share: true` 字段
   - 确认 front matter 格式正确（YAML 或 TOML）

2. **检查文件格式**
   - 文件必须是 `.md` 扩展名
   - 文件编码必须是 UTF-8

3. **检查文件路径**
   - 确认文件不在隐藏目录（以 `.` 开头）

## 📝 注意事项

1. **隐私保护**：确保不要在要分享的文章中包含敏感信息
2. **Token 安全**：不要将 Personal Access Token 提交到代码仓库
3. **同步频率**：避免设置过于频繁的同步，以免消耗 GitHub Actions 配额
4. **文件冲突**：如果手动修改了博客仓库中的文章，下次同步时会被覆盖

## 🔗 相关链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Hugo 文档](https://gohugo.io/documentation/)
- [Obsidian 文档](https://help.obsidian.md/)

## 📧 支持

如有问题，请在博客仓库中创建 Issue。