import codecs
import time
import sys
import copy
import traceback
from datetime import datetime
import xml.etree.ElementTree as ET
from model import TeamStatisticLine, PlayerStatisticLine, get_informations_from_root, get_fouls

def get_best_player_from_team_line(players, teams_dict):
    best_players_dict = dict()
    for player in players:
        if(player.teamname not in best_players_dict):
            best_players_dict[player.teamname] = player
        elif(player.eval >= best_players_dict[player.teamname].eval):
            best_players_dict[player.teamname] = player
    return best_players_dict

def save_best_players_to_file(players, teams_dict, path_to_save):
    best_players = get_best_player_from_team_line(players, teams_dict)
    for key, value in teams_dict.items():
        with codecs.open(f"{path_to_save}/{value}_best_player.txt", "a", "utf-8") as myfile:
            myfile.truncate(0)
            myfile.write(key)
            player = best_players[key]
            myfile.write(f"\n{player.number} {player.name} {player.surname} {player.points} pkt. {player.eval} eval {player.fgm2}/{player.fga2} za 2 {player.fgm3}/{player.fga3} za 3 {player.rebounds} zb. {player.assists} as. {player.steals} prz.")

def save_players_to_file(players, teams, path_to_save):
    teams_dict = dict()

    for counter, team in enumerate(teams):
        teams_dict[team.teamname] = "druzyna_" + str(counter)
        key = team.teamname
        value = "druzyna_" + str(counter)
        with codecs.open(f"{path_to_save}/{value}.txt", "a", "utf-8") as myfile:
            myfile.truncate(0)
            myfile.write(key)
        with codecs.open(f"{path_to_save}/{value}_players_oncourt.txt", "a", "utf-8") as myfile:
            myfile.truncate(0)
            myfile.write(key)
        with codecs.open(f"{path_to_save}/{value}_players_stats.txt", "a","utf-8") as myfile:
            myfile.truncate(0)
            myfile.write(key)
        with codecs.open(f"{path_to_save}/{value}_team_stats.txt", "a", "utf-8") as myfile:
            myfile.truncate(0)
            myfile.write(key)
            myfile.write(f"\n{team.defensive_rebounds}")
            myfile.write(f"\n{team.offensive_rebounds}")
            myfile.write(f"\n{team.assists}")
            myfile.write(f"\n{team.steals}")
            myfile.write(f"\n{team.turnovers}")
            myfile.write(f"\n{team.fgm2}/{team.fga2}")
            myfile.write(f"\n{team.fgm3}/{team.fga3}")
            myfile.write(f"\n{team.large_lead}")
            myfile.write(f"\n{team.pts_bench}")
            myfile.write(f"\n{team.pts_fastb}")
            myfile.write(f"\n{team.pts_paint}")
            myfile.write(f"\n{team.pts_ch2}")
            myfile.write(f"\n{team.pts_to}")
            
    for player in players:
        with codecs.open(f"{path_to_save}/{teams_dict[player.teamname]}.txt", "a", "utf-8") as myfile:
            myfile.write(f"\n{player.number} {player.name} {player.surname}")
        with codecs.open(f"{path_to_save}/{teams_dict[player.teamname]}_players_stats.txt", "a", "utf-8") as myfile:
            myfile.write(f"\n{player.number} {player.name} {player.surname} {player.minutes}:00 minut, {player.points} pkt. {player.fgm}/{player.fga} z gry {player.rebounds} zb. {player.assists} as. {player.steals} prz. ")  
        if(player.oncourt):
            with codecs.open(f"{path_to_save}/{teams_dict[player.teamname]}_players_oncourt.txt", "a", "utf-8") as myfile:
                myfile.write(f"\n{player.number} {player.name} {player.surname}")
    return teams_dict

def save_date_to_file(date, path_to_save):
    with codecs.open(f"{path_to_save}/data.txt", "a", "utf-8") as myfile:
        myfile.truncate(0)
        myfile.write(f"{date}")

def save_fouls_to_files(foul_1, foul_2, path_to_save):
    with codecs.open(f"{path_to_save}/druzyna_0_fouls.txt", "a", "utf-8") as myfile:
        myfile.truncate(0)
        myfile.write(str(foul_1))
    with codecs.open(f"{path_to_save}/druzyna_1_fouls.txt", "a", "utf-8") as myfile:
        myfile.truncate(0)
        myfile.write(str(foul_2))

def make_log(text):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return f'{dt_string}\t{text}'

def scan(scan_time, file_path, path_to_save):
    while(True):
        try:
            time.sleep(scan_time)
            scan_procedure(scan_time, file_path, path_to_save)
            print(make_log("Uaktualniono"))
        except FileNotFoundError:
            print(make_log(f"Plik .xml nie istnieje - {traceback.format_exc()}"))
        except Exception:
            print(make_log(f"Coś nie tak - {traceback.format_exc()}"))

def save_informations_to_files(players, teams, date, path_to_save):
    save_date_to_file(date, path_to_save)
    teams_dict = save_players_to_file(players, teams, path_to_save)
    save_best_players_to_file(players, teams_dict, path_to_save)

def scan_procedure(scan_time, file_path, path_to_save):
    tree = ET.parse(file_path)
    players, teams, date = get_informations_from_root(tree.getroot())
    foul_1, foul_2 = get_fouls(tree)


    player_copy = copy.deepcopy(players[0])
    player_copy.blocks = 5
    player_copy.assists = 10
    player_copy.points = 12
    print(f"\n\n{players[0].__dict__.items() ^ player_copy.__dict__.items()}")

    save_fouls_to_files(foul_1, foul_2, path_to_save)
    save_informations_to_files(players, teams, date, path_to_save)



if __name__ == "__main__":
    if(len(sys.argv)!=4):
        print("Podaj okres odświeżania, lokalizację pliku XML i lokalizację do zapisu plików txt!")
        sys.exit(1)
    try:
        scan(int(sys.argv[1]), sys.argv[2], sys.argv[3]) 
    except ValueError:
        print("Niepoprawny okres odświeżania!")
        sys.exit(1)