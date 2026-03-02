import os
import re
import yaml
import requests
import datetime
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TISTORY_ACCESS_TOKEN = os.getenv("TISTORY_ACCESS_TOKEN")
TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME", "datavalua")

API_BASE_URL = "https://www.tistory.com/apis"

class TistoryScheduler:
    def __init__(self, access_token, blog_name):
        self.access_token = access_token
        self.blog_name = blog_name

    def upload_image(self, image_path):
        """Uploads a local image to Tistory and returns the remote URL & replacer string."""
        url = f"{API_BASE_URL}/post/attach"
        path = Path(image_path)
        
        if not path.exists():
            print(f"Warning: Image not found at {image_path}")
            return None

        files = {'uploadedfile': open(path, 'rb')}
        params = {
            'access_token': self.access_token,
            'blogName': self.blog_name,
            'output': 'json'
        }
        
        try:
            response = requests.post(url, params=params, files=files)
            data = response.json()
            if response.status_code == 200 and 'tistory' in data:
                return data['tistory']['url']
            else:
                print(f"Failed to upload image {image_path}: {data}")
        except Exception as e:
            print(f"Error uploading image {image_path}: {e}")
        return None

    def process_content_images(self, content, base_dir):
        """Finds markdown image syntax, uploads images, and replaces links."""
        # Regex to find ![alt](images/...)
        img_pattern = r'!\[([^\]]*)\]\((images/[^\)]+)\)'
        
        def replacer(match):
            alt_text = match.group(1)
            local_rel_path = match.group(2)
            local_abs_path = base_dir / local_rel_path
            
            print(f"Found image: {local_rel_path}, uploading...")
            remote_url = self.upload_image(local_abs_path)
            
            if remote_url:
                # Tistory wants the URL directly or in an <img> tag for better results
                # But it usually wraps it in a special [##_Image_..._##] code if using their specific attach API
                # However, returning the absolute URL usually works in Markdown mode.
                return f'![{alt_text}]({remote_url})'
            return match.group(0) # Fallback to original if failed

        return re.sub(img_pattern, replacer, content)

    def publish_post(self, title, content, tags, date_str):
        """Publishes a post to Tistory via API."""
        url = f"{API_BASE_URL}/post/write"
        
        # Determine visibility (3: public, 0: private)
        visibility = 3 
        
        params = {
            'access_token': self.access_token,
            'blogName': self.blog_name,
            'title': title,
            'content': content,
            'tag': tags,
            'visibility': visibility,
            'category': 0, # Default category
            'output': 'json'
        }
        
        # If date is in the past, Tistory API usually sets the published time
        # if the published parameter is passed. 
        # Note: Tistory API date format is Unix timestamp or specific string?
        # Usually it takes 'published' as a unix timestamp.
        if date_str:
            # Convert YYYY-MM-DD to unix timestamp
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            # Set to a specific time (e.g., 09:00:00) to avoid midnight issues
            dt = dt.replace(hour=9, minute=0, second=0)
            params['published'] = int(dt.timestamp())

        try:
            response = requests.post(url, data=params)
            data = response.json()
            if response.status_code == 200:
                post_url = data.get('tistory', {}).get('url')
                print(f"Successfully published: {title} -> {post_url}")
                return True
            else:
                print(f"Failed to publish {title}: {data}")
        except Exception as e:
            print(f"Error publishing {title}: {e}")
        return False

    def run_scheduler(self, posts_dir):
        posts_path = Path(posts_dir)
        md_files = sorted(list(posts_path.glob("*.md")))
        
        for md_file in md_files:
            print(f"\n--- Processing {md_file.name} ---")
            with open(md_file, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            # Extract frontmatter
            parts = re.split(r'^---$', raw_text, flags=re.MULTILINE)
            if len(parts) >= 3:
                metadata = yaml.safe_load(parts[1])
                content = parts[2].strip()
            else:
                print(f"Skipping {md_file.name}: YAML frontmatter not found.")
                continue
            
            title = metadata.get('title', md_file.stem)
            date_str = metadata.get('date')
            tags = metadata.get('tags', '')
            
            # 1. Process images
            final_content = self.process_content_images(content, md_file.parent)
            
            # 2. Publish
            self.publish_post(title, final_content, tags, date_str)
            
            # Avoid hitting rate limits too hard
            time.sleep(2)

if __name__ == "__main__":
    if not TISTORY_ACCESS_TOKEN:
        print("Error: TISTORY_ACCESS_TOKEN not found in environment variables.")
    else:
        scheduler = TistoryScheduler(TISTORY_ACCESS_TOKEN, TISTORY_BLOG_NAME)
        scheduler.run_scheduler("posts")
