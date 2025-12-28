#!/usr/bin/env python3
"""
从 Obsidian 仓库同步文章到 Hugo 博客
只同步 front matter 中包含 share: true 的文章
"""

import os
import re
import shutil
import yaml
from pathlib import Path
from datetime import datetime

# 配置
OBSIDIAN_VAULT_PATH = Path("obsidian-vault")
HUGO_CONTENT_PATH = Path("content/posts")
OBSIDIAN_POSTS_PATH = OBSIDIAN_VAULT_PATH  # 可以根据你的 Obsidian 结构调整

def extract_frontmatter(content):
    """提取 YAML front matter"""
    # 支持 +++ 和 --- 两种格式
    patterns = [
        (r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n', 'toml'),
        (r'^---\s*\n(.*?)\n---\s*\n', 'yaml')
    ]
    
    for pattern, fmt in patterns:
        match = re.match(pattern, content, re.DOTALL)
        if match:
            frontmatter_text = match.group(1)
            body = content[match.end():]
            
            try:
                if fmt == 'yaml':
                    frontmatter = yaml.safe_load(frontmatter_text)
                else:  # toml
                    # 简单的 TOML 解析（对于基本的 key = value 格式）
                    frontmatter = {}
                    for line in frontmatter_text.split('\n'):
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            # 尝试转换布尔值
                            if value.lower() == 'true':
                                value = True
                            elif value.lower() == 'false':
                                value = False
                            frontmatter[key] = value
                
                return frontmatter, body, fmt
            except Exception as e:
                print(f"解析 front matter 失败: {e}")
                return None, content, None
    
    return None, content, None

def should_share(frontmatter):
    """检查文章是否应该分享"""
    if not frontmatter:
        return False
    
    # 检查 share 字段
    share = frontmatter.get('share', False)
    if isinstance(share, str):
        share = share.lower() in ['true', 'yes', '1']
    
    return bool(share)

def convert_to_hugo_format(content, frontmatter, original_format):
    """转换为 Hugo 格式的 front matter"""
    if not frontmatter:
        frontmatter = {}
    
    # 确保必要的字段存在
    if 'date' not in frontmatter or frontmatter.get('date') in ['YYYY-MM-DDTHH:mm:ssZ', '', None]:
        frontmatter['date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    
    if 'draft' not in frontmatter:
        frontmatter['draft'] = False
    
    # 确保有标题
    if 'title' not in frontmatter or not frontmatter.get('title'):
        # 从文件名生成标题（在调用处传入）
        frontmatter['title'] = 'Untitled'
    
    # 移除 share 字段（这是 Obsidian 特有的）
    frontmatter.pop('share', None)
    
    # 处理嵌套字段（如 cover.image）
    processed_frontmatter = {}
    nested_fields = {}
    
    for key, value in frontmatter.items():
        if '.' in key:
            # 处理嵌套字段，如 cover.image
            parts = key.split('.', 1)
            parent_key = parts[0]
            child_key = parts[1]
            
            if parent_key not in nested_fields:
                nested_fields[parent_key] = {}
            nested_fields[parent_key][child_key] = value
        else:
            processed_frontmatter[key] = value
    
    # 构建 Hugo 格式的 front matter（使用 TOML 格式）
    hugo_frontmatter = "+++\n"
    
    # 先写入普通字段
    for key, value in processed_frontmatter.items():
        if isinstance(value, bool):
            hugo_frontmatter += f"{key} = {str(value).lower()}\n"
        elif isinstance(value, (int, float)):
            hugo_frontmatter += f"{key} = {value}\n"
        elif isinstance(value, list):
            # 格式化列表
            list_str = str(value).replace("'", '"')
            hugo_frontmatter += f"{key} = {list_str}\n"
        elif value and value != 'None':
            # 字符串需要加引号，跳过空值和 'None'
            escaped_value = str(value).replace("'", "\\'")
            hugo_frontmatter += f"{key} = '{escaped_value}'\n"
    
    # 写入嵌套字段（使用 TOML 表格语法）
    for parent_key, children in nested_fields.items():
        hugo_frontmatter += f"\n[{parent_key}]\n"
        for child_key, value in children.items():
            if isinstance(value, bool):
                hugo_frontmatter += f"{child_key} = {str(value).lower()}\n"
            elif isinstance(value, (int, float)):
                hugo_frontmatter += f"{child_key} = {value}\n"
            elif isinstance(value, list):
                list_str = str(value).replace("'", '"')
                hugo_frontmatter += f"{child_key} = {list_str}\n"
            elif value and value != 'None':
                escaped_value = str(value).replace("'", "\\'")
                hugo_frontmatter += f"{child_key} = '{escaped_value}'\n"
    
    hugo_frontmatter += "+++\n"
    
    return hugo_frontmatter + content

def process_markdown_file(file_path, relative_path):
    """处理单个 Markdown 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, body, fmt = extract_frontmatter(content)
        
        # 检查是否应该分享
        if not should_share(frontmatter):
            return False, f"跳过（未标记为分享）: {relative_path}"
        
        # 如果没有标题，从文件名生成
        if not frontmatter or 'title' not in frontmatter or not frontmatter.get('title'):
            if not frontmatter:
                frontmatter = {}
            # 从文件名生成标题（去掉 .md 扩展名）
            frontmatter['title'] = relative_path.stem
        
        # 转换为 Hugo 格式
        hugo_content = convert_to_hugo_format(body, frontmatter, fmt)
        
        # 确定目标路径 - 只使用文件名，不保留目录结构
        target_path = HUGO_CONTENT_PATH / relative_path.name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(hugo_content)
        
        return True, f"✅ 同步成功: {relative_path.name}"
        
    except Exception as e:
        return False, f"❌ 处理失败 {relative_path}: {str(e)}"

def sync_posts():
    """同步所有文章"""
    print("🚀 开始同步 Obsidian 文章到 Hugo 博客...")
    print(f"📂 Obsidian 路径: {OBSIDIAN_VAULT_PATH}")
    print(f"📂 Hugo 内容路径: {HUGO_CONTENT_PATH}")
    print("-" * 60)
    
    if not OBSIDIAN_VAULT_PATH.exists():
        print(f"❌ 错误: Obsidian 仓库路径不存在: {OBSIDIAN_VAULT_PATH}")
        return
    
    # 确保目标目录存在
    HUGO_CONTENT_PATH.mkdir(parents=True, exist_ok=True)
    
    # 统计
    total_files = 0
    synced_files = 0
    skipped_files = 0
    error_files = 0
    
    # 遍历 Obsidian 仓库中的所有 Markdown 文件
    for md_file in OBSIDIAN_VAULT_PATH.rglob("*.md"):
        # 跳过隐藏文件和特殊目录
        if any(part.startswith('.') for part in md_file.parts):
            continue
        
        total_files += 1
        relative_path = md_file.relative_to(OBSIDIAN_VAULT_PATH)
        
        success, message = process_markdown_file(md_file, relative_path)
        print(message)
        
        if success:
            synced_files += 1
        elif "跳过" in message:
            skipped_files += 1
        else:
            error_files += 1
    
    # 输出统计信息
    print("-" * 60)
    print(f"📊 同步统计:")
    print(f"   总文件数: {total_files}")
    print(f"   ✅ 成功同步: {synced_files}")
    print(f"   ⏭️  跳过: {skipped_files}")
    print(f"   ❌ 失败: {error_files}")
    print("-" * 60)
    
    if synced_files > 0:
        print(f"🎉 同步完成！共同步 {synced_files} 篇文章")
    else:
        print("ℹ️  没有需要同步的文章")

if __name__ == "__main__":
    sync_posts()