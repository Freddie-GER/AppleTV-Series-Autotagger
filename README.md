# TV Series Auto Tagger

A Python application for automatically tagging TV series files with correct metadata using Mistral AI API and TVDB APIs. Built with PyQt6 for a modern, drag-and-drop enabled interface.

## Features

- Modern GUI with drag-and-drop support
- Smart filename parsing using OpenAI
- Metadata fetching from TVDB
- Multi-language tag support
- iTunes/Apple TV compatible tagging
- Artwork management

## Get you own Mistral API Key

- https://mistral.ai/api/
Select the experimental Tier, that one is free.

## Setup

We like to use Conda to manage our Python environment!
In any case, you need to have Python 3.11 installed, if running in an environment or not.

1. Create and activate the Conda environment:
```bash
conda create -n SeriesTagger python=3.11
conda activate SeriesTagger
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.template .env
```
Then edit `.env` with your API keys.

## Development

Project structure:
- `src/gui/`: GUI components
- `src/services/`: API integrations (OpenAI, TVDB)
- `src/utils/`: Helper functions
- `tests/`: Test files

## License

MIT License 