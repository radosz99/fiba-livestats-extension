# Table of Contents
- [General info](#desc)
- [Run](#run)  
  - [Python script](#script)  
  - [Executable](#exec)  
- [Features](#features)  
  - [Project structure](#structure)  
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
$ python app.py <path/to/config.json>
```

<a name="exec"></a>
## PyInstaller Executable
``` 
$ git clone https://github.com/radosz99/statistic-xml-reader-v2.git && cd statistic-xml-reader-v2
$ pip install -r requirements.txt
$ pip install pyinstaller
$ pyinstaller scanner.spec
$ cd dist
$ scanner.exe <path/to/config.json>

```

<p align="center">
  <img src="https://i.imgur.com/zoHdcIm.png" width=90% alt="Img"/>
</p>

 <a name="features"></a>
# Features

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

