import asyncio
import json
import csv

import numpy as np
import pandas as pd
import seaborn as sns

from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_text
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt

from scipy.stats import f_oneway


class API():

    def __init__(self, loop):
        # asyncio
        self.loop = loop
        self.session = None
        self.ENDPOINT = {
            # https://www.nba.com/stats/players/traditional
            "playersIndex": {"url": "https://stats.nba.com/stats/playerindex",
                             "params": {"College": "", "Country": "", "DraftPick": "", "DraftRound": "",
                                        "DraftYear": "", "Height": "", "Historical": "1", "LeagueID": "00",
                                        "Season": "2022-23", "SeasonType": "Regular Season", "TeamID": "0",
                                        "Weight": ""}},
            # https://www.nba.com/player/1630173/precious-achiuwa/profile
            "playerprofilev2": {"url": "https://stats.nba.com/stats/playerprofilev2",
                                "params": {'PlayerID': "", 'PerMode': "Per36", 'LeagueID': "00"}},
            # https://www.nba.com/player/1630173/precious-achiuwa/profile
            "commonplayerinfo": {"url": "https://stats.nba.com/stats/commonplayerinfo",
                                 "params": {"LeagueID": "00", "PlayerID": ""}},
            # https://www.nba.com/stats/players/shooting
            "shooting": {"url": "https://stats.nba.com/stats/leaguedashplayershotlocations",
                         "params": {"College": "", "Conference": "", "Country": "", "DateFrom": "", "DateTo": "",
                                    "DistanceRange": "5ft Range", "Division": "", "DraftPick": "", "DraftYear": "",
                                    "GameScope": "", "GameSegment": "", "Height": "", "LastNGames": "0", "Location": "",
                                    "MeasureType": "Base", "Month": "0", "OpponentTeamID": "0", "Outcome": "",
                                    "PORound": "0", "PaceAdjust": "N", "PerMode": "PerGame", "Period": "0",
                                    "PlayerExperience": "", "PlayerPosition": "", "PlusMinus": "N", "Rank": "N",
                                    "Season": "2022-23", "SeasonSegment": "", "SeasonType": "Regular Season",
                                    "ShotClockRange": "", "StarterBench": "", "TeamID": "0", "VsConference": "",
                                    "VsDivision": "", "Weight": ""}},
            "playerdashboardbyyearoveryear": {"url": "https://stats.nba.com/stats/playerdashboardbyyearoveryear",
                                              "params": {"PlayerID": "", "LastNGames": "0", "MeasureType": "Base",
                                                         "Month": "0", "OpponentTeamID": "0", "PaceAdjust": "N",
                                                         "PerMode": "PerGame", "Period": "0", "PlusMinus": "N",
                                                         "Rank": "N", "Season": "2022-23",
                                                         "SeasonType": "Regular Season", "DateFrom": "", "DateTo": "",
                                                         "GameSegment": "", "LeagueID": "00", "Location": "",
                                                         "Outcome": "", "PORound": "0", "SeasonSegment": "",
                                                         "ShotClockRange": "", "VsConference": "", "VsDivision": ""}},
        }

    async def start_session(self):
        import aiohttp
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
        try:
            await self.api.start_session()
        except Exception as e:
            print(f"Error Starting Session : {'{}: {}'.format(type(e).__name__, e)}")

    async def get_nba_data(self, endpoint, params={}):
        # Get NBA Data
        try:
            response = await self.api.get_data(endpoint, params)
            return response

        except Exception as e:
            print(f"Error API : {'{}: {}'.format(type(e).__name__, e)}")

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

        # # get 10 first players
        # commonplayersinfo = []
        # for id in range(len(person_ids)):

        #     commonplayerinfo = await self.get_nba_data("commonplayerinfo", {"PlayerID": person_ids[id]})
        #     commonplayersinfo.append(commonplayerinfo)
        #     #sleep
        #     await asyncio.sleep(3)

        # print(f"commonplayerinfo : Received {len(commonplayersinfo)} players\n")

        # # save to json
        # await self.api.save_data(commonplayersinfo, "commonplayersinfo.json")

        # # get 10 first players
        i = 0
        playerdashboardbyyearoveryear = []
        for id in range(len(person_ids)):
            print(i)
            i += 1
            playerdashboardbyyearoveryear.append(
                await self.get_nba_data("playerdashboardbyyearoveryear", {"PlayerID": person_ids[id]}))
            # sleep
            await asyncio.sleep(2)

        print(f"playerdashboardbyyearoveryear : Received {len(playerdashboardbyyearoveryear)} players\n")

        # save to json
        await self.api.save_data(playerdashboardbyyearoveryear, "playerdashboardbyyearoveryear.json")

    async def desicion_tree(self):
        # open playerdashboardbyyearoveryear.json
        with open('data/playerdashboardbyyearoveryear.json') as f:
            data = json.load(f)
        headers = data["infor"][0]["resultSets"][0]["headers"]

        headers[66] = "Winrate"

        with open('data/NbaData.csv', 'w') as f:
            dw = csv.DictWriter(f, delimiter=',', fieldnames=headers)
            dw.writeheader()

            writer = csv.writer(f)
            for elements in data["infor"]:
                try:
                    if elements["resultSets"][0]["rowSet"][0][8] >= 0.5:
                        elements["resultSets"][0]["rowSet"][0][66] = 1
                    else:
                        elements["resultSets"][0]["rowSet"][0][66] = 0
                    writer.writerow(elements["resultSets"][0]["rowSet"][0])

                except Exception as e:
                    pass

        file = pd.read_csv("data/NbaData.csv")
        # print("Data shape: ", file.shape)

        training = file.iloc[:, 9:-32].values
        # print("training : \n", training)
        # print("\n")
        targets = file.iloc[:, -1].values

        # print("targets : \n", targets)

        model_tree = DecisionTreeClassifier()
        model_tree.fit(training, targets)

        ft_names = list(file.columns)
        for i in range(9):
            ft_names.pop(0)
        for i in range(32):
            ft_names.pop(-1)

        text_representation = export_text(model_tree, feature_names=ft_names)
        fig = plt.figure(figsize=(100, 100))
        _ = plot_tree(model_tree, feature_names=ft_names,
                      filled=True, fontsize=30)

        plt.savefig('data/decision_tree.png')
        plt.show()

    async def plot_plots(self):
        with open("data/commonplayersinfo.json", "r") as f:
            commonPlayersInfo = json.load(f)
        with open("data/playerdashboardbyyearoveryear.json", "r") as g:
            shooting = json.load(g)

        # Get the player's id
        id_player = []
        for player in commonPlayersInfo["all_common_players"]:
            id_player.append(player["resultSets"][0]["rowSet"][0][0])

        # ------------------- STATISTICS FROM THE FILE: PLAYER DASHBOARD BY YEAR OVER YEAR ------------------------------
        # Offensive rebounds
        offensive_rebounds = []
        # Defensive rebounds
        defensive_rebounds = []
        # Assists
        assists = []
        # Blocks
        blocks = []
        # Steals
        steals = []
        # Minutes
        minutes = []
        # Points
        points = []
        # Field Goal Percentage
        field_goal_percentage = []
        # Free Throw Percentage
        free_throw_percentage = []
        # 3 Point Field Goal Percentage
        three_point_field_percentage = []

        # We extract different scores of the player's who have played in 2021-22 and of whom we have the characteristics in
        # the common players info file
        identification = []
        for ident in id_player:
            for i in shooting["infor"]:
                try:
                    if ident == i["parameters"]["PlayerID"]:
                        if (i["resultSets"][1]["rowSet"][1][1] == "2021-22") & (
                                i["resultSets"][1]["rowSet"][1][9] > 15):
                            minutes.append((i["resultSets"][1]["rowSet"][1][9]))

                            offensive_rebounds.append(i["resultSets"][1]["rowSet"][1][19])
                            defensive_rebounds.append(i["resultSets"][1]["rowSet"][1][20])
                            assists.append(i["resultSets"][1]["rowSet"][1][22])
                            steals.append(i["resultSets"][1]["rowSet"][1][24])
                            blocks.append(i["resultSets"][1]["rowSet"][1][25])
                            points.append(i["resultSets"][1]["rowSet"][1][29])
                            field_goal_percentage.append(i["resultSets"][1]["rowSet"][1][12] * 100)
                            free_throw_percentage.append(i["resultSets"][1]["rowSet"][1][18] * 100)
                            three_point_field_percentage.append(i["resultSets"][1]["rowSet"][1][15] * 100)

                            identification.append(i["parameters"]["PlayerID"])
                            break
                except Exception as e:
                    pass

        # ----------------------------- PLAYER'S CHARACTERISTICS FROM THE FILE: COMMON PLAYERS INFO ---------------------
        # Number of the player's jersey
        jersey_numbers = []
        # Position played in the game
        position = []
        # Player's team
        team = []
        # Player's height
        height_players = []
        # Player's weight
        weight_players = []
        # Player's birthdate
        birthdate = []
        # Player's nationality
        nationalities = []
        # Player's age
        age = []

        # We extract the player's characteristics that have played in 2021-22
        for i in identification:
            for player in commonPlayersInfo["all_common_players"]:
                if i == player["resultSets"][0]["rowSet"][0][0]:
                    jersey_numbers.append(int(player["resultSets"][0]["rowSet"][0][14]))
                    position.append(player["resultSets"][0]["rowSet"][0][15])
                    team.append(player["resultSets"][0]["rowSet"][0][19])
                    height_players.append((int(player["resultSets"][0]["rowSet"][0][11][0]) * 12 + int(
                        player["resultSets"][0]["rowSet"][0][11][-1])) * 2.54)
                    weight_players.append((int(player["resultSets"][0]["rowSet"][0][12]) * 0.453592))
                    birthdate.append(player["resultSets"][0]["rowSet"][0][7])
                    nationalities.append(player["resultSets"][0]["rowSet"][0][9])

        for i in birthdate:
            i = str(i)
            i = i.split("-")
            i[2] = i[2][:-9]
            x = 2021 - int(i[0])
            age.append(x)

        df = pd.DataFrame({"offensive_rebounds": offensive_rebounds, "defensive_rebounds": defensive_rebounds,
                           "assists": assists, "blocks": blocks, "steals": steals, "points": points,
                           "field_goal_percentage": field_goal_percentage,
                           "free_throw_percentage": free_throw_percentage,
                           "three_point_field_percentage": three_point_field_percentage,
                           "jersey_numbers": jersey_numbers,
                           "position": position, "team": team, "height_players": height_players,
                           "weight_players": weight_players, "nationalities": nationalities, "age": age})

        ############################################################################################################
        # ------------------------------------ PREDEFINED PLOTS  --------------------------------------------------
        ############################################################################################################

        # 1#  NUMBER OF POINTS by SIZE OF PLAYER ###
        plt.subplot(1, 2, 1)
        plt.scatter(height_players, points)
        plt.xlabel("Height")
        plt.ylabel("Points")
        plt.title("Points by height")

        plt.subplot(1, 2, 2)
        sns.heatmap(np.corrcoef(height_players, points), annot=True)
        plt.title("Correlation between height and points")
        plt.show()

        category_group_lists = df.groupby('height_players')['points'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between height and points is: ', anova_results[1])

        plt.boxplot(height_players)
        plt.xlabel("Height")
        plt.title("Distribution of player's heights")
        plt.show()

        # The conclusion we can draw is that, although at first you may think differently,
        # the fact of being taller does not mean that it is easier to score more points.
        # In fact, normally, the players who usually define the games by scoring more points are the point guards,
        # who do not stand out for their height. In addition, this graph shows that most of the players are
        # in a height range between 1.90 and 2.05m. To better visualize this statistic, we will use a boxplot.

        # We can see that the pearson coefficient between both variables is -0.016 (it could be said that it is null),
        # so the correlation is insignificant.

        # 2#  NUMBER OF POINTS by PLAYER'S NUMBER

        plt.subplot(1, 2, 1)
        plt.scatter(jersey_numbers, points)
        plt.xlabel("Jersey numbers")
        plt.ylabel("Points")
        plt.title("Points by jersey number")

        plt.subplot(1, 2, 2)
        sns.heatmap(np.corrcoef(jersey_numbers, points), annot=True)
        plt.title("Correlation between points and jersey numbers")
        plt.show()
        category_group_lists = df.groupby('jersey_numbers')['points'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between jersey numbers and points is: ', anova_results[1])

        # As expected, the fact that you wear a certain number on your T-shirt
        # is not going to make you score more points. Therefore, the correlation between these
        # variables (0.16) is insignificant.
        # A curious fact is that the players, even though they can choose numbers between 0 and 99,
        # most of them choose numbers less than 25. This curiosity can be seen more clearly
        # in the following histogram

        plt.hist(jersey_numbers, bins=100)
        plt.xlabel("Jersey numbers")
        plt.title("Jersey number count")
        plt.xticks(range(0, 100, 5))
        plt.title("Most common jersey numbers chosen by players")
        plt.show()

        # 3# FIELD GOAL PERCENTAGE by AGE
        plt.subplot(1, 2, 1)
        plt.scatter(age, field_goal_percentage)
        plt.xlabel("Age")
        plt.ylabel("Field goal percentage")
        plt.title("Field goal percentage by age")
        plt.subplot(1, 2, 2)
        sns.heatmap(np.corrcoef(age, field_goal_percentage), annot=True)
        plt.title("Correlation between field goal percentage and age")
        plt.show()
        category_group_lists = df.groupby('age')['field_goal_percentage'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between field goal percentage and age is: ', anova_results[1])

        # Although it may seem that the fact of having more experience is something significant
        # when it comes to having more success in the shots, the reality is that there are young
        # players with more talent and success in shots than the more experienced ones

        # 4 OFFENSIVE REBOUNDS by HEIGHT
        plt.subplot(1, 2, 1)
        plt.scatter(height_players, offensive_rebounds)
        plt.xlabel("Height")
        plt.ylabel("Offensive rebounds")
        plt.title("Offensive rebounds by height")
        plt.subplot(1, 2, 2)
        sns.heatmap(np.corrcoef(height_players, offensive_rebounds), annot=True)
        plt.title("Correlation between offensive rebounds and height")
        plt.show()
        category_group_lists = df.groupby('offensive_rebounds')['blocks'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between offensive rebounds and height is: ', anova_results[1])

        # Although the correlation of both parameters (0.27) is not significant as it is less than 0.5,
        # it can be said that there is a certain relationship between the player's height and
        # the amount of rebounds he grabs. This is due to the fact that the tactical positioning
        # is also important when it comes to grabbing a rebound, not only the height.

        # 5 BLOCKS by WEIGHT
        plt.subplot(1, 2, 1)
        plt.scatter(weight_players, blocks)
        plt.xlabel("Weight")
        plt.ylabel("Blocks")
        plt.title("Blocks by weight")
        plt.subplot(1, 2, 2)
        sns.heatmap(np.corrcoef(weight_players, blocks), annot=True)
        plt.title("Correlation between blocks and weight")
        plt.show()
        category_group_lists = df.groupby('weight_players')['blocks'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between weight and number of blocks is: ', anova_results[1])

        # It can be seen from the results obtained that the correlation between the weight of the player
        # and the blocks made is considerably high. Anyone would have thought that the best
        # blockers would be the tallest, however, this is not the case since the most important variable that affects
        # the number of blocks made by the player is the weight

        # 6# BLOCKS BY POSITION
        sns.jointplot(x=position, y=blocks)
        plt.xlabel("Position")
        plt.ylabel("Blocks")
        plt.show()
        category_group_lists = df.groupby('position')['blocks'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between position played and number of blocks is: ', anova_results[1])

        # The p-value between these two variables is really low which means, that we can reject the null hypothesis. This
        # means that there is an observable relation between these two variables. Thanks to the p-value we can say that the
        # position the player plays and the number of blocks he makes per game are related to each other.
        # In the join plot we can observe that the players who make the most amount of blocks are the ones who play center and
        # center-forward followed by forward-center. It can also be observed that playing one position determines the number of
        # blocks the player is going to be able to make since the points are not distributed from the maximum value to the
        # minimum but rather concentrated in one area.
        # Thanks to the join plot we can see the amount of points that are hidden underneath each other since only having the
        # scatter plot may lead us to think there are fewer players than there actually are. This is fixed with the uni-variable
        # histogram shown on the right hand side of the scatter plot.

        # 7# NUMBER OF STEALS BY HEIGHT
        plt.subplot(1, 2, 1)
        plt.scatter(height_players, steals)
        plt.xlabel("Height")
        plt.ylabel("Steals")
        plt.title("Steals by height")
        plt.subplot(1, 2, 2)
        sns.heatmap(np.corrcoef(height_players, steals), annot=True)
        plt.title("Correlation between steals and height")
        plt.show()
        category_group_lists = df.groupby('height_players')['steals'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between height and number of steals is: ', anova_results[1])

        plt.subplot(1, 2, 1)
        plt.scatter(weight_players, steals)
        plt.xlabel("Weight")
        plt.ylabel("Steals")
        plt.title("Steals by weight")
        plt.subplot(1, 2, 2)
        sns.heatmap(np.corrcoef(weight_players, steals), annot=True)
        plt.title("Correlation between steals and weight")
        plt.show()
        category_group_lists = df.groupby('weight_players')['steals'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between weight and number of steals is: ', anova_results[1])

        sns.jointplot(x=position, y=steals)
        plt.xlabel("Position")
        plt.ylabel("Steals")
        plt.show()

        category_group_lists = df.groupby('position')['steals'].apply(list)
        anova_results = f_oneway(*category_group_lists)
        print('P-Value for Anova between position and number of steals is: ', anova_results[1])

        # The same thing happens as with height and points, the two variables have a low number of correlation so no conclusions
        # can be made with this graphics and between these two variables.
        # Aso between weight and steals, even though there is a correlation between the weight and the blocks, there is not when
        # it comes to steals and weight. However, there is a correlation between the position and the number of steals made by
        # a player, being the two positions who make the most steals the Forward and the guard

        # -------------------------------------------- INTERFACE ---------------------------------------------
        while True:
            print(f"Do you want to plot any more variables? [y/n]")
            yon = input()
            if yon != "y" and yon != "n":
                print("You didn't introduce the right answer. Please enter [y/n]")
                continue
            else:
                break

        if yon == "y":
            while True:
                print(f"Which player's characteristic do you want to plot?")
                print(f"1) Height")
                print(f"2) Weight")
                print(f"3) Country")
                print(f"4) Position")
                print(f"5) Team")
                print(f"6) Jersey number")
                print(f"7) Age")
                characteristic = input()
                if int(characteristic) > 7 or int(characteristic) < 1:
                    print("Please enter a number between 1 and 7")
                    continue
                else:
                    break

            if characteristic == "1":
                decisionChar = height_players
                x = f'{height_players=}'.split('=')[0]
            elif characteristic == "2":
                decisionChar = weight_players
                x = f'{weight_players=}'.split('=')[0]
            elif characteristic == "3":
                decisionChar = nationalities
                x = f'{nationalities=}'.split('=')[0]
            elif characteristic == "4":
                decisionChar = position
                x = f'{position=}'.split('=')[0]
            elif characteristic == "5":
                decisionChar = team
                x = f'{team=}'.split('=')[0]
            elif characteristic == "6":
                decisionChar = jersey_numbers
                x = f'{jersey_numbers=}'.split('=')[0]
            elif characteristic == "7":
                decisionChar = age
                x = f'{age=}'.split('=')[0]

            while True:
                print(f"Which player's statistics do you want to plot?")
                print(f"1) Points")
                print(f"2) Assists")
                print(f"3) Offensive Rebounds")
                print(f"4) Defensive Rebounds")
                print(f"5) Blocks")
                print(f"6) Steals")
                print(f"7) Field goal percentage")
                print(f"8) Free throw percentage")
                print(f"9) Three point field percentage")
                stadistic = input()

                if int(stadistic) < 1 or int(stadistic) > 9:
                    print("Please enter a number between 1 and 9")
                    continue
                else:
                    break

            if stadistic == "1":
                decisionStat = points
                y = f'{points=}'.split('=')[0]
            elif stadistic == "2":
                decisionStat = assists
                y = f'{assists=}'.split('=')[0]
            elif stadistic == "3":
                decisionStat = offensive_rebounds
                y = f'{offensive_rebounds=}'.split('=')[0]
            elif stadistic == "4":
                decisionStat = defensive_rebounds
                y = f'{defensive_rebounds=}'.split('=')[0]
            elif stadistic == "5":
                decisionStat = blocks
                y = f'{blocks=}'.split('=')[0]
            elif stadistic == "6":
                decisionStat = steals
                y = "Steals"
            elif stadistic == "7":
                decisionStat = field_goal_percentage
                y = "field_goal_percentage"
            elif stadistic == "8":
                decisionStat = free_throw_percentage
                y = "free_throw_percentage"
            elif stadistic == "9":
                decisionStat = three_point_field_percentage
                y = "three_point_field_percentage"

            if (decisionChar == position) | (decisionChar == team) | (decisionChar == nationalities):
                while True:
                    print(f"Which plot type do you want to use?")
                    print(f"1) Scatter plot")
                    print(f"2) Histogram")
                    print(f"3) Join-plot")
                    plot_type = input()
                    if int(plot_type) < 1 or int(plot_type) > 3:
                        print("Please enter a number between 1 and 3")
                        continue
                    else:
                        break

            else:
                while True:
                    print(f"Which plot type do you want to use?")
                    print(f"1) Scatter plot")
                    print(f"2) Histogram")
                    print(f"3) Join-plot")
                    print(f"4) Box-plot")
                    print(f"5) Correlation")
                    plot_type = input()
                    if int(plot_type) < 1 or int(plot_type) > 5:
                        print("Please enter a number between 1 and 3")
                        continue
                    else:
                        break

            if plot_type == "1":
                plt.subplot(1, 2, 1)
                plt.scatter(decisionChar, decisionStat)
                plt.xlabel(x)
                plt.ylabel(y)
                plt.subplot(1, 2, 2)
                sns.heatmap(np.corrcoef(decisionStat, decisionChar), annot=True)
                plt.show()
            elif plot_type == "2":
                plt.subplot(1, 2, 1)
                plt.hist(decisionChar)
                plt.xlabel(x)
                plt.title(x + " count")
                plt.subplot(1, 2, 2)
                plt.hist(decisionStat)
                plt.xlabel(y)
                plt.title(y + " count")
                plt.show()
            elif plot_type == "3":
                sns.jointplot(x=decisionChar, y=decisionStat)
                plt.xlabel(x)
                plt.ylabel(y)
                plt.show()
                category_group_lists = df.groupby(x)[y].apply(list)
                anova_results = f_oneway(*category_group_lists)
                print('P-Value for Anova is: ', anova_results[1])

                if (anova_results[1] < 0.05):
                    print("We can reject the null hypothesis. The two variables are related to each other.")
                else:
                    print("We cannot reject the null hypothesis. The two variables are not related to each other.")

            elif plot_type == "4":
                plt.subplot(1, 2, 1)
                plt.boxplot(decisionChar)
                plt.xlabel(x)
                plt.subplot(1, 2, 2)
                plt.boxplot(decisionStat)
                plt.xlabel(y)
                plt.show()
            elif plot_type == "5":
                sns.heatmap(np.corrcoef(decisionStat, decisionChar), annot=True)
                plt.show()

    async def main(self):
        # await self.ddos_api()

        await self.desicion_tree()
        await self.plot_plots()


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
