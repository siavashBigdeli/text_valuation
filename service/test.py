import time
from concurrent.futures import ThreadPoolExecutor
import requests


def make_request(num):
    response = requests.get("https://httpbin.org/ip")
    # print(f"Request {num}: {response.json()}")

def main():
    futures = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(100):
            futures.append(executor.submit(make_request, i))
    
    for future in futures:
        print(future.result())

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    print(f"Elapsed run time: {end_time - start_time} seconds.")
