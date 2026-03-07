import os
import re
from pathlib import Path

POSTS_DIR = r"c:\Users\Choi\Desktop\antigravity\signal\posts"

def get_title(filepath):
    if not filepath:
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'^title:\s*["\']?(.*?)["\']?$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "포스팅"

def process_file_list(md_files):
    valid_files = []
    for f in md_files:
        basename = os.path.basename(f)
        if re.match(r'^\d{4}-\d{2}-\d{2}\.md$', basename):
            valid_files.append(f)
    valid_files.sort()
    
    for i, filepath in enumerate(valid_files):
        prev_file = valid_files[i-1] if i > 0 else None
        next_file = valid_files[i+1] if i < len(valid_files) - 1 else None
        process_single_file(filepath, prev_file, next_file)

def process_single_file(filepath, prev_file, next_file):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
    if len(parts) < 3:
        print(f"Skipped (No frontmatter): {filepath}")
        return

    frontmatter = parts[1]
    body = '---'.join(parts[2:])

    # 1. Description
    body_no_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    body_no_html = re.sub(r'<[^>]*>', '', body_no_code)
    body_no_images = re.sub(r'!\[.*?\]\(.*?\)', '', body_no_html)
    body_no_links = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', body_no_images)
    
    lines = [line.strip() for line in body_no_links.split('\n')]
    text_content = ""
    for line in lines:
        if line and not line.startswith('#') and not line.startswith('*') and not line.startswith('-'):
            text_content += line + " "
    
    description = text_content[:150].strip()
    if len(text_content) > 150:
        description += "..."
    description = description.replace('\n', ' ').replace('"', "'")

    if 'description:' not in frontmatter:
        frontmatter = frontmatter.rstrip() + f'\ndescription: "{description}"\n'
    else:
        frontmatter = re.sub(r'description:.*', f'description: "{description}"', frontmatter)

    # 2. TOC
    headings = []
    lines = body.split('\n')
    in_code = False
    for line in lines:
        if line.startswith('```'):
            in_code = not in_code
        if not in_code:
            m = re.match(r'^(#{2,3})\s+(.*)', line)
            if m:
                level = len(m.group(1))
                title_raw = m.group(2).strip()
                slug = title_raw.lower().replace(' ', '-')
                slug = re.sub(r'[^a-zA-Z0-9가-힣\-]', '', slug)
                headings.append((level, title_raw, slug))
    
    has_toc = False
    toc_lines = ["\n> **목차**\n"]
    for level, title, slug in headings:
        indent = "  " * (level - 2)
        toc_lines.append(f"{indent}- [{title}](#{slug})")
        has_toc = True
    toc_lines.append("\n")
    toc_str = "\n".join(toc_lines)

    if has_toc and "목차" not in body:
        first_h2_idx = -1
        in_code = False
        for idx, line in enumerate(lines):
            if line.startswith('```'):
                in_code = not in_code
            if not in_code and line.startswith('## '):
                first_h2_idx = idx
                break
        
        if first_h2_idx != -1:
            lines.insert(first_h2_idx, toc_str)

    # 3. Internal Links
    if "⬅️ **이전 글" not in body and "➡️ **다음 글" not in body:
        footer_lines = []
        if prev_file:
            prev_title = get_title(prev_file)
            prev_basename = os.path.basename(prev_file)
            footer_lines.append(f"⬅️ **이전 글:** [{prev_title}](./{prev_basename})")
        
        if next_file:
            next_title = get_title(next_file)
            next_basename = os.path.basename(next_file)
            footer_lines.append(f"➡️ **다음 글:** [{next_title}](./{next_basename})")
        
        if footer_lines:
            if len(lines) >= 2 and lines[-1].strip() != "---" and lines[-2].strip() != "---":
                lines.append("\n---")
            lines.append("\n" + "\n\n".join(footer_lines) + "\n")

    new_body = '\n'.join(lines)
    new_content = f"---{frontmatter}---{new_body}"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Advanced SEO Applied: {os.path.basename(filepath)}")

if __name__ == '__main__':
    md_files = [str(p) for p in Path(POSTS_DIR).glob('*.md')]
    process_file_list(md_files)
