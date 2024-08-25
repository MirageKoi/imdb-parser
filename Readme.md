# IMDb Parser

This project contains a Python script (`main.py`) that parses IMDb web site. The script is designed to extract and process information from IMDb, such as movie titles, ratings, and other relevant details.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)

## Installation

To get started with this project, you'll need to clone the repository and set up your environment.

1. **Clone the repository:**

```sh
git clone https://github.com/MirageKoi/imdb-parser.git
cd imdb-parser
```
Set up a Python virtual environment:

It's recommended to use a virtual environment to manage dependencies.

```sh
python3 -m venv venv
source venv/bin/activate
```
Install the required dependencies
If there is a requirements.txt file provided, install the dependencies:

```sh
pip install -r requirements.txt
```
## Usage
Once you've set up your environment and installed the dependencies, you can run the script.

Running the Script:
You can run the script directly using Python:

```sh
python3 main.py
```
Alternatively, you can use the provided shell script to ensure all dependencies are installed and the environment is properly configured:

```sh
./run_parser.sh
```

This will start the IMDb parsing process and generate two csv files with top movies and actors.

## Dependencies
The script requires the following Python libraries:

```sh
 aiohttp
 beautifulsoup4
 pandas
 lxml
```