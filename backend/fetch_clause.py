import httpx
import re

def get_scan_clause():
    url = "https://chartink.com/screener/ipo-base-scan-4"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = httpx.get(url, headers=headers)
    print("Status:", resp.status_code)
    
    # Try to extract the scan clause from HTML
    match = re.search(r'name="scan_clause"\s+value="(.*?)"', resp.text)
    if match:
        print("Found scan_clause in input:")
        print(match.group(1))
    
    # Try to extract from javascript
    match2 = re.search(r"scan_clause\s*:\s*['\"](.*?)['\"]", resp.text)
    if match2:
        print("Found scan_clause in JS:")
        print(match2.group(1))
        
    # Another approach
    match3 = re.search(r"data-scan-clause=['\"](.*?)['\"]", resp.text)
    if match3:
        print("Found scan_clause in data attribute:")
        print(match3.group(1))
        
    # Print a large chunk around the word scan_clause
    idx = resp.text.find('scan_clause')
    if idx != -1:
        print("Context around scan_clause:")
        print(resp.text[max(0, idx-100):idx+500])

if __name__ == "__main__":
    get_scan_clause()
