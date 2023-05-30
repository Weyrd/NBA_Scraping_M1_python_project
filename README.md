# NBA_Scraping_M1_python_project

We need to scrape data from the NBA website.

If you want to code and try some things, you have two options:

1. Create a new .py file in the same folder and use the .json file in the data directory. You can import it using the following code:

   ```py
   # open commonplayersinfo.json
   with open("data/commonplayersinfo.json", "r") as f:
       commonplayersinfo = json.load(f)
   ```

 

2. Alternatively, you can code directly in the project.py file. The code should be implemented between lines 118 and 140. Please note that it may be challenging, but I have provided an example below to retrieve the jersey numbers of ten players:

   ```py
   # Example code to retrieve jersey numbers
   for player in players:
       jersey_number = player["jersey_number"]
       print(jersey_number)
   ```

   Feel free to explore different ideas, such as plotting the number of points based on player size, analyzing the impact of player numbers on game performance, or predicting the percentage of game wins during clutch moments based on the average weight of players on the team.

   Remember, this project also involves utilizing Selenium for web scraping, making API requests, and applying basic machine learning techniques.

