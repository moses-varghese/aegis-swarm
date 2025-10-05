import sys
import http.client

try:
    # Use http.client for a lightweight, dependency-free check
    conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
    conn.request("GET", "/")
    response = conn.getresponse()
    
    # The server is healthy if it returns a 200 OK status
    if response.status == 200:
        print("Healthcheck passed.")
        sys.exit(0)
    else:
        print(f"Healthcheck failed with status code: {response.status}")
        sys.exit(1)
except Exception as e:
    print(f"Healthcheck failed with exception: {e}")
    sys.exit(1)
finally:
    if 'conn' in locals():
        conn.close()