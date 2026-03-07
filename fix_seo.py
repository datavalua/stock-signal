import os
import re
import glob
import yaml

POSTS_DIR = r"c:\Users\Choi\Desktop\antigravity\signal\posts"

def process_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter and body
    parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = '---'.join(parts[2:])
        
        try:
            metadata = yaml.safe_load(frontmatter)
            tags = metadata.get('tags', [])
            title = str(metadata.get('title', '포스팅')).replace('"', '')
        except Exception:
            tags = []
            title = '포스팅'
            
        # Standardize tags
        if isinstance(tags, str):
            tags_list = [t.strip() for t in tags.split(',')]
        elif isinstance(tags, list):
            tags_list = [str(t).strip() for t in tags]
        else:
            tags_list = []
        
        tags_list = [t for t in tags_list if len(t) > 0 and t != ',']
        tags_str = ", ".join(tags_list)
        
        lines = body.split('\n')
        new_lines = []
        in_code_block = False

        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
                new_lines.append(line)
                continue
                
            if not in_code_block:
                # 1. Header adjustment (don't increment if already at level 2-4)
                if line.startswith('#'):
                    if line.startswith('# '):
                        new_lines.append('#' + line)
                    else:
                        new_lines.append(line)
                
                # 2. Image Alt tags
                elif '![' in line:
                    line = re.sub(r'!\[\]\(', f'![{title} 관련 이미지](', line)
                    line = re.sub(r'!\[image\]\(', f'![{title} 관련 이미지](', line)
                    line = re.sub(r'!\[img\]\(', f'![{title} 관련 이미지](', line)
                    new_lines.append(line)
                    
                # 3. Skip existing mechanical intro if it exists (for re-runs)
                elif line.startswith('**핵심 키워드:'):
                    continue
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
                
        new_body = '\n'.join(new_lines).strip()
        new_content = f"---{frontmatter}---{new_body}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Processed: {os.path.basename(filepath)}")
    else:
        print(f"Skipped (No frontmatter): {os.path.basename(filepath)}")

if __name__ == '__main__':
    md_files = glob.glob(os.path.join(POSTS_DIR, '*.md'))
    for f in md_files:
        process_markdown_file(f)
