import os
import glob
import re
import yaml

POSTS_DIR = r"c:\Users\Choi\Desktop\antigravity\signal\posts"

def fix_mangled_keywords():
    for filepath in glob.glob(os.path.join(POSTS_DIR, '*.md')):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
        if len(parts) >= 3:
            frontmatter = parts[1]
            try:
                metadata = yaml.safe_load(frontmatter)
                tags = metadata.get('tags', [])
            except Exception:
                tags = []
                
            if isinstance(tags, str):
                if tags.startswith('[') and tags.endswith(']'):
                    tags = tags[1:-1].replace("'", "").replace('"', "")
                tags_str = tags
            elif isinstance(tags, list):
                tags_str = ", ".join(tags)
            else:
                tags_str = ""
                
            if tags_str:
                new_content = re.sub(
                    r'\*\*핵심 키워드:.*?\*\* \| 이 글에서는', 
                    f'**핵심 키워드: {tags_str}** | 이 글에서는', 
                    content,
                    count=1
                )
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Fixed: {os.path.basename(filepath)}")

if __name__ == '__main__':
    fix_mangled_keywords()
