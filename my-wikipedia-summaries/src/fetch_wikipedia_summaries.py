import aiohttp
import asyncio
import json
from typing import List, Optional

SPECIES_LIST = [
    "Homo sapiens",
    "Panthera leo",
    "Elephas maximus",
    "Gorilla gorilla",
    "Canis lupus familiaris"
]

def truncate_to_words(text: str, max_words: int) -> str:
    words = text.split()
    return ' '.join(words[:max_words]) + ('...' if len(words) > max_words else '')

async def fetch_summary(session: aiohttp.ClientSession, species: str, retries: int = 3) -> Optional[dict]:
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{species.replace(' ', '_')}"
    for attempt in range(retries):
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error fetching {species}: {response.status}")
        except Exception as e:
            print(f"Exception for {species}: {e}")
    return None

async def collect_summaries(species_list: List[str], concurrency: int) -> List[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for species in species_list:
            tasks.append(fetch_summary(session, species))
        return await asyncio.gather(*tasks)

def load_species_from_file(path: str) -> List[str]:
    with open(path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Wikipedia summaries for species.")
    parser.add_argument('--input', type=str, help='Path to the file containing species names.')
    parser.add_argument('--output', type=str, help='Path to the output JSON file.')
    parser.add_argument('--concurrency', type=int, default=5, help='Number of concurrent requests.')

    args = parser.parse_args()

    species_list = load_species_from_file(args.input) if args.input else SPECIES_LIST

    summaries = asyncio.run(collect_summaries(species_list, args.concurrency))

    with open(args.output, 'w') as outfile:
        json.dump(summaries, outfile, indent=4)

if __name__ == "__main__":
    main()