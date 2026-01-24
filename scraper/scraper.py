import asyncio
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from aiolimiter import AsyncLimiter

MAX_RATE_SECOND = 5
TIME_LIMIT_SECONDS = 1
rate_limit = AsyncLimiter(MAX_RATE_SECOND, TIME_LIMIT_SECONDS)
URL = "https://eu.finalfantasyxiv.com/lodestone/character/"

async def scrape(session: ClientSession, url: str):
    async with rate_limit:
        async with session.get(url) as response:
            data = {}
            try:
                if response.status == 404:
                    pass
                elif response.status == 403:
                    pass
                else:
                    website_text = await response.text()
                    soup = BeautifulSoup(website_text, "html.parser")
                    data.update({"name": soup.find(name="p", class_="frame__chara__name").text})
                    data.update({"world": soup.find(name="p", class_="frame__chara__world").text})

                    # Title may not always be set for the player
                    try:
                        data.update({"title": soup.find(name="p", class_="frame__chara__title").text})
                    except AttributeError:
                        pass

                    player_details = soup.select('div.character__profile__data__detail div.character-block__box')
                    for detail in player_details:
                        # Free company is optional data and has a different tag
                        if detail.select('div.character__freecompany__name h4 a'):
                            fc_name = detail.select('div.character__freecompany__name h4 a')[0].text
                            data.update({"fc": fc_name})
                        # PVP team is optional data and has a different tag
                        elif detail.select('div.character__pvpteam__name h4 a'):
                            pvp_name = detail.select('div.character__pvpteam__name h4 a')[0].text
                            data.update({"pvp": pvp_name})
                        else:
                            ps = detail.find_all("p")
                            key = ps[0].text
                            value = ps[1].text
                            data.update({key: value})

                    player_levels = soup.select('div.character__level__list ul li')
                    for player_level_element in player_levels:
                        player_level = player_level_element.text
                        player_class = player_level_element.find('img')['data-tooltip']
                        data.update({player_class: player_level})
            except Exception as ex:
                print(f"Failed scraping data for url: '{url}': {ex}")
                data.update({"error": "scraping error"})
            return data

async def local_main():
    async with ClientSession() as session:
        tasks = []
        for i in range(1, 20):
            tasks.append(
                scrape(session, URL + str(i))
            )
        result = await asyncio.gather(*tasks, return_exceptions=True)
        print(result)

if __name__ == "__main__":
    asyncio.run(local_main())