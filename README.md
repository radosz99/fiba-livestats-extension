# Table of Contents
- [General info](#desc)
- [Run](#run)  
  - [Python script](#script)  
  - [Executable](#exec)  
- [Setup](#setup)  
- [Features](#features)  
- [Status](#stat)  


<a name="desc"></a>
# General info


<a name="run"></a>
# Run

<a name="script"></a>
## Python script
```
$ git clone https://github.com/radosz99/statistic-xml-reader-v2.git && cd statistic-xml-reader-v2
$ pip install -r requirements.txt
$ python app.py <path/to/json/file>
```

<a name="exec"></a>
## PyInstaller Executable
``` 
$ git clone https://github.com/radosz99/statistic-xml-reader-v2.git && cd statistic-xml-reader-v2
$ pip install -r requirements.txt
$ pip install pyinstaller
$ pyinstaller scanner.spec
$ cd dist
$ scanner.exe <path/to/json/file>

```


 <a name="setup"></a>
# Setup

## JSON with parameters
All parameters can be set in JSON file to which path is given as a first and only one argument when starting the script.
```
{
    "server": {
        "ip": "12.345.67.89",
        "username": "test_user",
        "xml_path": "/home/stats/game.xml",
        "private_key_path": "keys\\xml_stats_key",
        "password": "123456"
    },
    "local_xml_path": "C:\\Users\\Test\\game.xml",
    "save_directory_path": "C:\\,
    "resources_path": "C:\\resources",
    "fontname": "RobotoMono-SemiBold",
    "scan_times": {"fouls": -1, "players_oncourt": -1, "teams_stats": 2, "best_players": -1,
        "random_stat": 2, "players_stats": 4, "team_points": -1, "period_number": -1, "quarter_time": 1
    },
    "probabilities": {
        "team" : 1,
        "player" : 3,
        "player_stats": {"fga2": 4, "fga3": 4, "fta": 4, "blocks": 2, "steals": 5, "assists": 6,
            "rebounds": 4, "offensive_rebounds": 4, "defensive_rebounds": 0, "fouls": 1, "turnovers": 6,
        },
        "team_stats": {"fga2": 4, "fga3": 4, "fta": 4, "blocks": 2,	"steals": 5, "assists": 6, "rebounds": 4,
            "offensive_rebounds": 4, "defensive_rebounds": 0, "fouls": 1, "turnovers": 6, "pts_fastb": 3,
            "pts_bench": 3, "pts_paint": 3, "pts_ch2": 3
        }
    }
}
```

 <a name="features"></a>
# Features
<p align="center">
  <img src="https://github.com/radosz99/statistic-xml-reader-v2/blob/master/screens/player_random_stat.png" width=50% alt="Img"/>
</p>

<p align="center">
  <img src="https://github.com/radosz99/statistic-xml-reader-v2/blob/master/screens/player_stats.png" width=110% alt="Img"/>
</p>

<p align="center">
  <img src="https://github.com/radosz99/statistic-xml-reader-v2/blob/master/screens/team_stats.png" width=110% alt="Img"/>
</p>



 <a name="structure"></a>
## Project structure
```
statistic-xml-reader-v2/
|
├── resources/
|   |── photos/
|      |── druzyna_0_logo.png
|      |── druzyna_1_logo.png
|      |── den_nikola_jokic.png
|      |── ...
|      |── bos_kemba_walker.png
|   |── fonts/
|      |── RobotoMono-Bold.ttf
|   |── templates/
|      |── player_stats.png
|
├── app.py
├── model.py
├── scanner.spec
├── config.json
├── README.md
├── requirements.txt
```

 <a name="stat"></a>
# Status

