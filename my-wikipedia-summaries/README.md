# My Wikipedia Summaries

This project is designed to fetch summaries from Wikipedia for a specified list of species using the Wikipedia REST API. The script utilizes asynchronous programming to efficiently collect data.

## Project Structure

```
my-wikipedia-summaries
├── src
│   └── fetch_wikipedia_summaries.py
├── requirements.txt
└── README.md
```

## Installation

To get started, clone the repository and install the required dependencies. You can do this by running:

```bash
pip install -r requirements.txt
```

## Usage

1. **Prepare a list of species**: Create a text file containing the names of the species you want to fetch summaries for, with one species name per line.

2. **Run the script**: Execute the script using Python. You can specify the path to your species file and the desired concurrency level. For example:

```bash
python src/fetch_wikipedia_summaries.py --species-file path/to/your/species.txt --concurrency 5
```

## Functions

- **truncate_to_words(text: str, max_words: int) -> str**: Truncates a given text to a specified number of words.

- **fetch_summary(session: aiohttp.ClientSession, species: str, retries: int) -> Optional[dict]**: Asynchronously fetches the summary of a species from the Wikipedia API, with retry logic.

- **collect_summaries(species_list: List[str], concurrency: int) -> List[dict]**: Asynchronously collects summaries for a list of species using concurrent requests.

- **load_species_from_file(path: str) -> List[str]**: Loads species names from a specified file.

- **main()**: The main function that sets up argument parsing, handles input/output, and orchestrates the fetching of summaries.

## Contributing

Contributions are welcome! If you have suggestions for improvements or additional features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.