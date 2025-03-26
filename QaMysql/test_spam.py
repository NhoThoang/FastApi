import httpx
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Function to send 100 requests
async def send_requests(session, num_requests):
    tasks = []
    for _ in range(num_requests):
        tasks.append(session.get("https://dsdaihoc.com/"))
        print("Request sent")
    await asyncio.gather(*tasks)

# Function to handle multiple rounds of requests
async def main():
    async with httpx.AsyncClient() as client:
        for _ in range(1000):  # Run 10 rounds of 100 requests each
            await send_requests(client, 10)

# Run the event loop
if __name__ == "__main__":
    asyncio.run(main())
