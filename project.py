import asyncio
import aiohttp
import json

import numpy as np
import pandas as pd
import seaborn as sns


class API():

    def __init__(self, loop):
        # asyncio
        self.loop = loop
        self.session = None
        self.ENDPOINT = {
            # https://www.nba.com/stats/players/traditional
            "playersIndex": {"url": "https://stats.nba.com/stats/playerindex", "params": {"College": "", "Country": "", "DraftPick": "", "DraftRound": "", "DraftYear": "", "Height": "", "Historical": "1", "LeagueID": "00", "Season": "2022-23", "SeasonType": "Regular Season", "TeamID": "0", "Weight": ""}},
            # https://www.nba.com/player/1630173/precious-achiuwa/profile
            "playerprofilev2": {"url": "https://stats.nba.com/stats/playerprofilev2", "params": {'PlayerID': "",'PerMode': "Per36",'LeagueID': "00"}},
            # https://www.nba.com/player/1630173/precious-achiuwa/profile
            "commonplayerinfo": {"url": "https://stats.nba.com/stats/commonplayerinfo", "params": {"LeagueID": "00", "PlayerID": ""}},
            # https://www.nba.com/stats/players/shooting
            "shooting": {"url": "https://stats.nba.com/stats/leaguedashplayershotlocations", "params": {"College": "", "Conference": "", "Country": "", "DateFrom": "", "DateTo": "", "DistanceRange": "5ft Range", "Division": "", "DraftPick": "", "DraftYear": "", "GameScope": "", "GameSegment": "", "Height": "", "LastNGames": "0", "Location": "", "MeasureType": "Base", "Month": "0", "OpponentTeamID": "0", "Outcome": "", "PORound": "0", "PaceAdjust": "N", "PerMode": "PerGame", "Period": "0", "PlayerExperience": "", "PlayerPosition": "", "PlusMinus": "N", "Rank": "N", "Season": "2022-23", "SeasonSegment": "", "SeasonType": "Regular Season", "ShotClockRange": "", "StarterBench": "", "TeamID": "0", "VsConference": "", "VsDivision": "", "Weight": ""}},
        }

    async def start_session(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv: 106.0) Gecko/20100101 Firefox/106.0",
            "Referer": "https://www.nba.com/",
        }
        self.session = aiohttp.ClientSession(headers=headers)


    async def get_data(self, endpoint, params):
        print(f"--- API\n  Getting data from {endpoint} with params {params}")
        url = self.ENDPOINT[endpoint]["url"]

        # add all params and replace the default ones
        params = {**self.ENDPOINT[endpoint]["params"], **params}
        url = url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

        print(f"  URL: {url}\n")

        async with self.session.get(url) as response:
            return await response.json()

    # save data to json indented
    async def save_data(self, data, filename):
        with open("data/" + filename, "w") as f:
            json.dump(data, f, indent=4)

 
    # clsoe session
    async def close_session(self):
        await self.session.close()


class Main():

    def __init__(self, api, loop):
        self.api = api
        self.loop = loop

    
    async def start_api_loop(self):
        try: await self.api.start_session()
        except Exception as e: print(f"Error Starting Session : {'{}: {}'.format(type(e).__name__, e)}")


    async def get_nba_data(self, endpoint, params={}):
        # Get NBA Data
        try:
            response = await self.api.get_data(endpoint, params)
            return response

        except Exception as e:print(f"Error API : {'{}: {}'.format(type(e).__name__, e)}")

    async def run(self):
        await self.start_api_loop()
        await self.main()
    
    def quit(self):
        self.loop.run_until_complete(self.api.close_session())
        self.loop.stop()
        self.loop.close()

    async def ddos_api(self):
        data = await self.get_nba_data("playersIndex")
        print(f"playersIndex : Received {len(data['resultSets'][0]['rowSet'])} players\n")

        # get all person id if 2022-23 season in TO_YEAR
        person_ids = [player[0] for player in data['resultSets'][0]['rowSet'] if int(
            player[24]) == 2022 or int(player[25]) == 2022]
        print(f"playersIndex : Received {len(person_ids)} players for 2022-23 season\n")

        # get 10 first players
        commonplayersinfo = []
        for id in range(10):
            commonplayerinfo = await self.get_nba_data("commonplayerinfo", {"PlayerID": person_ids[id]})
            commonplayersinfo.append(commonplayerinfo)

        print(f"commonplayerinfo : Received {len(commonplayersinfo)} players\n")

        # save to json
        # await self.api.save_data(commonplayersinfo, "commonplayersinfo.json")



    async def main(self):
        # await self.ddos_api()


        #########################
        #                       #
        #     YOUR CODE HERE    #
        #                       #
        #########################
        # example to get jersey number of player

        # open commonplayersinfo.json
        with open("data/commonplayersinfo.json", "r") as f:
            commonplayersinfo = json.load(f)

        # get jersey number
        jersey_numbers = []
        for player in commonplayersinfo["all_common_players"]:
            # you can check the structure of the json in the file commonplayersinfo.json (HEADER)
            jersey_numbers.append(player["resultSets"][0]["rowSet"][0][14])
        
        print(f"Jersey Numbers : {jersey_numbers}")

        # Get all shooting data for 2022-23 season (https://www.nba.com/stats/players/shooting)
        print("This function can take a while to complete the first time...")
        shooting = await self.get_nba_data("shooting", {"Season": "2022-23"})

        print(f"shooting : Received data of {len(shooting['resultSets']['rowSet'])} players\n")


        #########################
        #                       #
        #        END CODE       #
        #                       #
        #########################
        
        














        

# Run (don't touch)
if __name__ == "__main__":
    # new loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    api = API(loop)
    main = Main(api, loop)
    try:
        main.loop.run_until_complete(main.run())
    
    except Exception as e:
        print(f"Error Main : {'{}: {}'.format(type(e).__name__, e)}")
    finally:
        main.quit()

