- [General info](#desc)
- [Run](#run)  
  - [Python script](#script)  
  - [Executable](#exec)  
- [Setup](#setup)  
  - [XML file](#xml)  
  - [Save directory](#savedir)  
  - [Resources directory](#resources)  
- [Detail info](#detail)  
- [Status](#stat)  


<a name="desc"></a>
# General info
Application which helps to integrate video live stream from official Polish Basketball Association games with live stats from [Fiba Live Stats](https://geniussports.com/sports/sports-management/livestats/).   

It creates basic .txt files which can be read by OBS Studio (or any other live streaming software) and converted in many ways to show current result, time, quarter number or any statistics.

<a name="run"></a>
# Run

<a name="script"></a>
## Python script
```bash
$ git clone https://github.com/radosz99/statistic-xml-reader-v2.git && cd statistic-xml-reader-v2
$ pip install -r requirements.txt
$ python app.py <path/to/json/file>
```

<a name="exec"></a>
## PyInstaller Executable
``` bash
$ git clone https://github.com/radosz99/statistic-xml-reader-v2.git && cd statistic-xml-reader-v2
$ pip install -r requirements.txt
$ pip install pyinstaller
$ pyinstaller scanner.spec
$ cd dist
$ scanner.exe <path/to/json/file>

```

 <a name="setup"></a>
# Setup
All parameters and needed informations can be set in JSON file to which path is given as a first and only one argument when starting the script:
```javascript
{
    "local_xml_path": "C:\\Users\\Test\\game.xml",
    "save_directory_path": "C:\\save_directory",
    "resources_path": "C:\\resources",
    "fontname": "RobotoMono-SemiBold",
    "scan_times": {"fouls": -1, "players_oncourt": -1, "teams_stats": 2, "best_players": -1,
        "random_stat": 2, "players_stats": 4, "team_points": -1, "period_number": -1, "quarter_time": 1
    },
    "probabilities": {
        "team" : 1,
        "player" : 3,
        "player_stats": {"fga2": 4, "fga3": 4, "fta": 4, "blocks": 2, "steals": 5, "assists": 6,
            "rebounds": 4, "offensive_rebounds": 4, "defensive_rebounds": 0, "fouls": 1, "turnovers": 6
        },
        "team_stats": {"fga2": 4, "fga3": 4, "fta": 4, "blocks": 2, "steals": 5, "assists": 6, "rebounds": 4,
            "offensive_rebounds": 4, "defensive_rebounds": 0, "fouls": 1, "turnovers": 6, "pts_fastb": 3,
            "pts_bench": 3, "pts_paint": 3, "pts_ch2": 3
        }
    }
}
```
Parameters `scan_times` and `probabilities` will be discused in [Detail info](#detail) section.
 <a name="xml"></a>
## XML file
This is primary thing in application. In this file there are all statistics and plays from the game, and also additional information such as league or game date. Path to this file can be set in `local_xml_path` parameter in JSON file. To operate on this file there is a need to have it visible from computer on which live stream is working. There are two possible ways to do it:
1. Computer on which statistics are collected (*stats computer*) and computer on which live stream is working (*live stream computer*) are in the same network environment and `local_xml_path` is path to network location to XML file on *stats computer*,
2. If it is impossible to have both computer in the same network XML file can be send via SFTP by *stats computer* to remote server and *live stream computer* will download it constantly. In that case you must run `xml_sender.py` script on *stats computer* with this command:
```bash
$ python xml_sender.py <local/path/to/xml> <server/path/to/xml>
```
And you must update JSON file on *live stream computer* to add extra thread which will download XML constantly. Parameter that must be added it is `server` with any additional informations such as `ip`, `username`, remote `xml_path` and local `private_key_path` or `password` (or both).

:heavy_exclamation_mark: :heavy_exclamation_mark: :heavy_exclamation_mark: You can choose (depends on server) authentication method, if you leave both ways (`private_key_path` and `password`) program will try first to login by key and then by password if key is incorrect or doesn't found. :heavy_exclamation_mark: :heavy_exclamation_mark: :heavy_exclamation_mark:
```javascript
"server": {
    "ip": "12.345.67.89",
    "username": "test_user",
    "xml_path": "/home/stats/game.xml",
    "private_key_path": "C:\\rsa_keys\\xml_stats_key",
    "password": "123456"
    }
```
<a name="savedir"></a>
## Save directory
This is path to the folder where all .txt files with stats, graphics and photos will be saving.


 <a name="resources"></a>
## Resources directory
Another parameter from JSON file is path to resources directory - `resources_path`. Directory is obligate to have following structure:
```
resources/
|
|── photos/
|   |── druzyna_0_logo.png
|   |── druzyna_1_logo.png
|   |── den_nikola_jokic.png
|   |── ...
|   |── bos_kemba_walker.png
|
|── fonts/
|   |── RobotoMono-Bold.ttf
|   |── <any other fonts>
|
|── templates/
|   |── player_stats.png
|   |── <any other femplates>
|
```
In `photos` subdirectory you can put teams logos with names `druzyna_0_logo.png` and `druzyna_1_logo.png`, and also (this is optionally) players photos in `<team_shortname>_<name>_<surname>.png` format, e.g. `den_nikola_jokic.png`.  

In `fonts` subdirectory you can put whatever (monospaced are prefered) fonts you like and refer to any of it in JSON file in `fontname` parameter. It will be used in all created graphics.

In `templates` subdirectory there must be all needed templates, currently only one is used it is `player_stats.png` template.


 <a name="detail"></a>
# Detail info
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

