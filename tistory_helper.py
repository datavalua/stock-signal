import os
import pyperclip
import yaml
import subprocess
import time

def parse_md_post(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            header = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return header, body
    return None, content

def run_helper():
    posts_dir = r'c:\Users\Choi\Desktop\antigravity\signal\posts'
    images_dir = r'c:\Users\Choi\Desktop\antigravity\signal\posts\images'
    
    # Get all markdown files except test ones, sorted by date
    files = [f for f in os.listdir(posts_dir) if f.endswith('.md') and not f.startswith('9999')]
    files.sort()

    print("\n" + "="*50)
    print("   Tistory Semi-Auto Posting Helper (Series)   ")
    print("="*50)
    print(f"Total {len(files)} posts found in {posts_dir}\n")
    
    for i, filename in enumerate(files):
        print(f"{i+1:2d}. [{filename}]")

    print("\n" + "-"*50)
    start_idx = input(">> Start from which number? (Default: 1, 'q' to quit): ")
    if start_idx.lower() == 'q': return
    
    try:
        current_idx = int(start_idx) - 1 if start_idx else 0
    except ValueError:
        current_idx = 0

    while current_idx < len(files):
        filename = files[current_idx]
        file_path = os.path.join(posts_dir, filename)
        header, body = parse_md_post(file_path)
        
        if not header:
            print(f"\n[!] Skipping {filename}: No YAML frontmatter found.")
            current_idx += 1
            continue

        print("\n" + "*"*60)
        print(f"  NOW PROCESSING: {header.get('date')} ({filename})")
        print(f"  TITLE: {header.get('title')}")
        print("*"*60)

        # 1. Copy Title
        print(f"\n[Step 1/4] Copying TITLE...")
        input(f"   >> Press Enter to copy to clipboard...")
        pyperclip.copy(header.get('title', ''))
        print("   ✅ TITLE COPIED!")

        # 2. Copy Body
        print(f"\n[Step 2/4] Copying CONTENT (Markdown)...")
        input(f"   >> Press Enter to copy to clipboard...")
        pyperclip.copy(body)
        print("   ✅ CONTENT COPIED! (Please use 'Markdown' mode in Tistory)")

        # 3. Copy Tags
        print(f"\n[Step 3/4] Copying TAGS...")
        input(f"   >> Press Enter to copy to clipboard...")
        pyperclip.copy(header.get('tags', ''))
        print("   ✅ TAGS COPIED! (Paste in Tistory Tag field)")

        # 4. Open Images Folder
        print(f"\n[Step 4/4] Opening IMAGES folder...")
        input(f"   >> Press Enter to open folder for drag & drop...")
        if os.name == 'nt':
            os.startfile(images_dir)
        else:
            subprocess.run(['open', images_dir])
        
        print("\n" + "="*50)
        print(f"   PLEASE CHECK: Publication date should be {header.get('date')}")
        print("="*50)
        
        choice = input(f"\n>> Finished with {header.get('date')}? \n   (Enter: next, 'p': previous, 'm': back to menu, 'q': quit): ")
        
        if choice.lower() == 'q': break
        elif choice.lower() == 'p': current_idx = max(0, current_idx - 1)
        elif choice.lower() == 'm': return run_helper() # Restart
        else: current_idx += 1

    print("\nAll tasks completed. Good luck with your blog series!")

if __name__ == "__main__":
    try:
        run_helper()
    except KeyboardInterrupt:
        print("\nHelper stopped by user.")
    except Exception as e:
        print(f"\nError: {e}")
