#!/usr/bin/env python3
"""Optional local server launcher for testing AMDE interactive demos."""

import http.server
import os
import socketserver
import webbrowser

PORT = 8089

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    demo_dir = os.path.abspath(os.path.join(script_dir, "..", "demo"))
    os.chdir(demo_dir)

    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map.update({
        ".wasm": "application/wasm",
        ".js": "application/javascript",
        ".html": "text/html",
        ".css": "text/css",
    })

    print(f"Starting AMDE demo server at http://127.0.0.1:{PORT}")
    print(f"Serving directory: {demo_dir}")
    print("Press Ctrl+C to stop.")

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
