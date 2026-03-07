import os
import glob
import re

POSTS_DIR = r"c:\Users\Choi\Desktop\antigravity\signal\posts"

def remove_emojis_from_string(text):
    # Remove BMP symbols and dingbats (e.g., arrows, stars)
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    # Remove Supplemental Multilingual Plane emojis (e.g., rocket, robot, etc.)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    # Also remove some specific unicode characters if they were missed (like isolated regional indicator symbols)
    text = re.sub(r'[\u2B50\u2B55]', '', text) # some stars and circles
    
    # Fix potential double spaces created by removing emojis
    # We want to be careful not to break markdown formatting, so we mostly fix spaces around headings or lists
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        if line.startswith('#'):
            line = re.sub(r'^(#+)\s+', r'\1 ', line)
        if line.startswith('-'):
            line = re.sub(r'^-\s+', '- ', line)
        
        # Remove empty spaces at the end of headings
        if line.startswith('#'):
            line = line.strip()
            
        new_lines.append(line)
        
    return '\n'.join(new_lines)


def process_files():
    for filepath in glob.glob(os.path.join(POSTS_DIR, '*.md')):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = remove_emojis_from_string(content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Removed emojis from: {os.path.basename(filepath)}")

if __name__ == '__main__':
    process_files()
