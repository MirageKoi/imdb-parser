import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import logging


logger = logging.getLogger(__name__)


CAST_APPENDIX = "fullcredits/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
}

url_250 = "https://www.imdb.com/chart/top/"


async def fetch_page(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, headers=headers) as response:
        return await response.text()


async def parse_top_250_movies(page_text: str) -> dict[str, str]:
    soup = BeautifulSoup(page_text, "lxml")
    data = json.loads(soup.find("script", {"type": "application/ld+json"}).text)
    return {
        item["item"]["name"]: item["item"]["url"] for item in data["itemListElement"]
    }


def parse_movie_main_cast(page_text: str) -> dict[str, str]:
    soup = BeautifulSoup(page_text, "lxml")
    data = soup.find("table", class_="cast_list")
    cast = data.find_all("tr")
    result = {}
    for x in cast[1:]:
        if x.select(".castlist_label"):
            break
        actor_info = x.find_all("td")[1]
        result.update({actor_info.a.text.strip(): actor_info.a["href"].split("?")[0]})

    return result


async def retrieve_cast_for_all_movies() -> pd.DataFrame:
    async with aiohttp.ClientSession() as session:
        top_250_pages = await fetch_page(session, url_250)
        movie_data = await parse_top_250_movies(top_250_pages)

        tasks = []

        for movie, url in movie_data.items():
            tasks.append(fetch_page(session, url + CAST_APPENDIX))

        movie_cast_pages = await asyncio.gather(*tasks)

    extracted_data = [parse_movie_main_cast(film) for film in movie_cast_pages]

    data = []

    for movie, movie_url in zip(movie_data.keys(), extracted_data):
        for actor, actor_url in movie_url.items():
            data.append(
                {
                    "movie": movie,
                    "movie_link": movie_data[movie],
                    "actor": actor,
                    "actor_link": f"https://www.imdb.com{actor_url}",
                }
            )

    df = pd.DataFrame(data)

    return df


def parse_actor(page_text: str) -> dict[str, str | int]:
    soup = BeautifulSoup(page_text, "lxml")
    actor_name = soup.find("span", class_="hero__primary-text").text
    table_info = soup.find(id="accordion-item-actor-previous-projects") or soup.find(
        id="accordion-item-actress-previous-projects"
    )
    if table_info is None:
        raise TypeError(f"Info about actor movies is abscent. {actor_name =}")

    found_rates = table_info.find_all("span", class_="ipc-rating-star--rating")
    number_of_stars = len(found_rates)
    average_rate = sum([float(rate.text) for rate in found_rates]) // number_of_stars

    return {
        "actor": actor_name,
        "number_of_films": number_of_stars,
        "average_rate": average_rate,
    }


async def retrieve_info_about_popular_actors(links: set[str]) -> pd.DataFrame:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for link in links:
            tasks.append(fetch_page(session, link))

        actor_pages = await asyncio.gather(*tasks)

    extracted_data = []
    for page in actor_pages:
        try:
            extracted_data.append(parse_actor(page))
        except TypeError as exc:
            logger.error(f"Info about actor movies is abscent. {str(exc)}")
            continue

    return pd.DataFrame([record for record in extracted_data if record is not None])


def get_repeated_actor_from_pd_as_urls(pd: pd.DataFrame, gt_value: int = 1) -> set[str]:
    counts = pd.actor.value_counts()
    actors_met_criteria = pd[pd.actor.isin(counts.index[counts.gt(gt_value)])]
    return set(actors_met_criteria.actor_link.to_list())


async def main():
    df_movies_actors = await retrieve_cast_for_all_movies()
    df_subset = df_movies_actors[["movie", "actor"]]
    df_subset.to_csv("top_250_movies.csv", index=False)

    actor_links_to_parse = get_repeated_actor_from_pd_as_urls(df_movies_actors)
    df_popular_actors = await retrieve_info_about_popular_actors(actor_links_to_parse)
    df_popular_actors.to_csv("popular_actors.csv", index=False)


if __name__ == "__main__":
    logging.basicConfig(filename="logger.log", level=logging.INFO)
    asyncio.run(main())
