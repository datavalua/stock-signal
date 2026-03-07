import os
import glob
import re

POSTS_DIR = r"c:\Users\Choi\Desktop\antigravity\signal\posts"

def fix_truncated_description():
    for filepath in glob.glob(os.path.join(POSTS_DIR, '*.md')):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = re.split(r'^---\s*$', content, flags=re.MULTILINE)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = '---'.join(parts[2:])
            
            # Find current description
            match = re.search(r'^description:\s*["\'](.*?)["\']\s*$', frontmatter, re.MULTILINE)
            if match:
                current_desc = match.group(1)
                
                # Only fix if it ends with "..." artificially added by us
                if current_desc.endswith('...'):
                    # Regenerate text content
                    body_no_code = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
                    body_no_html = re.sub(r'<[^>]*>', '', body_no_code)
                    body_no_images = re.sub(r'!\[.*?\]\(.*?\)', '', body_no_html)
                    body_no_links = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', body_no_images)
                    
                    lines = [line.strip() for line in body_no_links.split('\n')]
                    text_content = ""
                    for line in lines:
                        if line and not line.startswith('#') and not line.startswith('*') and not line.startswith('-'):
                            text_content += line + " "
                    
                    text_content = text_content.replace('\n', ' ').replace('"', "'")
                    
                    # Target around 150 chars, but cut at a logical boundary (space or punctuation)
                    target_len = 150
                    if len(text_content) > target_len:
                        # Find the last space before the 150th character
                        cut_pos = text_content.rfind(' ', 0, target_len)
                        if cut_pos == -1:
                            cut_pos = target_len
                        
                        # Check if we cut off a word mid-sentence. We want words to refer to a coherent meaning. 
                        # To be safe, let's just use the cut_pos spaces and append ...
                        new_desc = text_content[:cut_pos].strip() + "..."
                        
                        # Replace in frontmatter
                        new_frontmatter = frontmatter.replace(f'description: "{current_desc}"', f'description: "{new_desc}"')
                        new_content = content.replace(frontmatter, new_frontmatter)
                        
                        if new_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"Fixed Description: {os.path.basename(filepath)}")

if __name__ == '__main__':
    fix_truncated_description()
