# Vercel Serverless Function for InstaCollect
# File: api/collect.py

from http.server import BaseHTTPRequestHandler
import json
import random

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read request body
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode('utf-8'))
        
        tag = data.get('tag', '')
        limit = data.get('limit', 5)
        
        # Generate dummy response (replace with real scraper later)
        posts = []
        for i in range(min(limit, 10)):
            post = {
                "url": f"https://www.instagram.com/p/DUMMY{i}/",
                "caption": f"Sample post about #{tag} - Post {i+1}",
                "likes": random.randint(100, 5000),
                "comments": random.randint(10, 500),
                "timestamp": "2026-02-14T10:00:00Z",
                "hashtags": [tag, "sample", "test"],
                "source_tag": tag
            }
            posts.append(post)
        
        response = {
            "status": "success",
            "tag": tag,
            "collected": len(posts),
            "data": posts
        }
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Send response
        self.wfile.write(json.dumps(response).encode())
        
    def do_OPTIONS(self):
        # Handle preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
