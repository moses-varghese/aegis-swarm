import sys
import http.client
import logging

# Configure basic logging for the healthcheck script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

try:
    # Use http.client for a lightweight, dependency-free check
    conn = http.client.HTTPConnection("localhost", 8000, timeout=5)
    conn.request("GET", "/")
    response = conn.getresponse()
    
    # The server is healthy if it returns a 200 OK status
    if response.status == 200:
        logging.info("Healthcheck passed with status code 200.")
        sys.exit(0)
    else:
        logging.error(f"Healthcheck failed with status code: {response.status}")
        sys.exit(1)
except Exception as e:
    logging.error(f"Healthcheck failed with exception: {e}", exc_info=True)
    sys.exit(1)
finally:
    if 'conn' in locals() and conn:
        conn.close()