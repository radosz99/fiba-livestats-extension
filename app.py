import codecs
import time
import threading
import json
import sys
import app
import signal
import copy
import random
import model
import math
from operator import attrgetter
import os
import logging
import traceback
from datetime import datetime
import xml.etree.ElementTree as ET
from model import TeamStatisticLine, PlayerStatisticLine, get_teams_from_xml, get_fouls, get_officials, get_date, get_value_from_list_of_tuples_by_key

thismodule = sys.modules[__name__]


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
path_to_save, xml_file_path = None, None
log = logging.getLogger("my-logger")

def get_best_player_from_team_line(team):
    return max(team.players, key=attrgetter('eval'))

def save_best_players_to_files():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        value = "druzyna_" + str(counter)
        player = get_best_player_from_team_line(team)
        write_one_line_to_file(f"{path_to_save}/{value}_best_player.txt", f"{team.teamname}\n{player.number} {player.name} {player.surname} {player.points} pkt. {player.eval} eval {player.fgm2}/{player.fga2} za 2 {player.fgm3}/{player.fga3} za 3 {player.rebounds} zb. {player.assists} as. {player.steals} prz.")
        
def write_one_line_to_file(path, text):
    with codecs.open(path, "a", "utf-8") as myfile:
        myfile.truncate(0)
        myfile.write(text)
        myfile.close()

def get_players_string(players):
    string = ''
    for player in players:
        string += f"\n{player.number} {player.name} {player.surname}"
    return string

def get_value_if_not_equals_to_zero(string, value):
    if(value != 0):
        return f"\t{value}"
    else:
        return f"\t"

def get_string_quarter(period):
    try:
        quarter_int = int(period)
    except ValueError:
        return 'OT'
    if(quarter_int <= 4):
        return f"{quarter_int}Q"
    else:
        return f"OT{quarter_int - 4}"


def get_players_stats_string(players):
    string = ''
    for player in players:
        string += f"\n{player.number} {player.name} {player.surname}"
        string += f"\t{player.points}\t{player.minutes}"
        if(player.fga2 != 0):
            string += f"\t{player.fgm2}/{player.fga2}"
            string += f"\t{round(player.fgm2/player.fga2*100,1)}%"
        else:
            string += f"\t\t0.0%"

        if(player.fga3 != 0):
            string += f"\t{player.fgm3}/{player.fga3}"
            string += f"\t{round(player.fgm3/player.fga3*100,1)}%"
        else:
            string += f"\t\t0.0%"

        if(player.fga != 0):
            string += f"\t{player.fgm}/{player.fga}"
            string += f"\t{round(player.fgm/player.fga*100,1)}%"
        else:
            string += f"\t\t0.0%"

        if(player.fta !=0):
            string += f"\t{player.ftm}/{player.fta}"
            string += f"\t{round(player.ftm/player.fta*100,1)}%"
        else:
            string += f"\t\t0.0%"
        
        string += get_value_if_not_equals_to_zero(string, player.offensive_rebounds)
        string += get_value_if_not_equals_to_zero(string, player.defensive_rebounds)
        string += get_value_if_not_equals_to_zero(string, player.rebounds)
        string += get_value_if_not_equals_to_zero(string, player.assists)
        string += get_value_if_not_equals_to_zero(string, player.fouls)
        string += get_value_if_not_equals_to_zero(string, player.turnovers)
        string += get_value_if_not_equals_to_zero(string, player.steals)
        string += get_value_if_not_equals_to_zero(string, player.blocks)
        string += f"\t{player.eval}"
    return string

def get_players_oncourt_string(players):
    string = ''
    for player in players:
        if(player.oncourt):
            string += f"\n{player.number} {player.name} {player.surname}"
    return string

def save_players_oncourt_to_file():
    teams = teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_players_oncourt.txt", f"{team.teamname}{get_players_oncourt_string(team.players)}")

def save_team_stats_to_file():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_team_stats.txt", f"{team.teamname}\n{team.defensive_rebounds}\n{team.offensive_rebounds}\n{team.assists}\n{team.steals}\n{team.turnovers}\n{team.fgm2}/{team.fga2}\n{team.fgm3}/{team.fga3}\n{team.large_lead}\n{team.pts_bench}\n{team.pts_fastb}\n{team.pts_paint}\n{team.pts_ch2}\n{team.pts_to}")

def save_players_stats_to_file():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_players_stats.txt", f"{team.teamname}{get_players_stats_string(team.players)}")

def save_players_to_file():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}.txt", f"{team.teamname}{get_players_string(team.players)}")
         
def save_date_to_file(date):
    write_one_line_to_file(f"{path_to_save}/data.txt", date)
    make_log("Zapisano datę")

def save_officials_to_file(officials):
    write_one_line_to_file(f"{path_to_save}/officials.txt", officials)
    make_log("Zapisano sędziów")

def save_team_names_to_files(teams):
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_name.txt", team.teamname)
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_id.txt", team.id)
    make_log("Zapisano nazwy oraz id drużyn")

def save_team_points_to_files():
    root = ET.parse(xml_file_path).getroot()
    for counter, linescore in enumerate(root.findall(f"./team/linescore")):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_score.txt", get_value_from_list_of_tuples_by_key(linescore.items(), 'score'))

def save_fouls_to_files():
    fouls = get_fouls(ET.parse(xml_file_path).getroot())
    for key, value in fouls.items():
        write_one_line_to_file(f"{path_to_save}/{key}_fouls.txt", str(value))

def save_quarter_to_file():
    root = ET.parse(xml_file_path).getroot()
    period = get_value_from_list_of_tuples_by_key(root.find('status').items(), 'period')
    write_one_line_to_file(f"{path_to_save}/period.txt", get_string_quarter(period))

def save_time_to_file():
    root = ET.parse(xml_file_path).getroot()
    period_time = get_value_from_list_of_tuples_by_key(root.find('status').items(), 'clock')
    status = False if get_value_from_list_of_tuples_by_key(root.find('status').items(), 'running') == 'F' else True
    if(not status):
        write_one_line_to_file(f"{path_to_save}/time.txt", period_time)
    else:
        try:
            with codecs.open(f"{path_to_save}/time.txt", "r", "utf-8") as myfile:
                old_time = myfile.readline()
            write_one_line_to_file(f"{path_to_save}/time.txt", decrement_time(old_time))
        except FileNotFoundError:
            write_one_line_to_file(f"{path_to_save}/time.txt", period_time)

    
def convert_from_quarter_time_to_seconds(quarter_time):
    old_time_list = quarter_time.split(':')
    minutes = int(old_time_list[0])
    seconds = int(old_time_list[1])
    return minutes * 60 + seconds

def convert_from_seconds_to_quarter_time(seconds_time):
    minutes = str(math.floor(seconds_time / 60))
    seconds = str(seconds_time % 60)
    if(len(minutes) == 1):
        minutes = f"0{minutes}"
    if(len(seconds) == 1):
        seconds = f"0{seconds}"
    return f"{minutes}:{seconds}"

def decrement_time(old_time):
    time_in_seconds = convert_from_quarter_time_to_seconds(old_time)
    if(time_in_seconds > 0):
        time_in_seconds -= 1
    return convert_from_seconds_to_quarter_time(time_in_seconds)

def make_log(text):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    log.info(f"{dt_string}\t{text}")

def make_difference_entries(player, differences_dict, prefix):
    return [getattr(model, f"get_{key}_stat")(prefix, value, player) for key, value in differences_dict.items()]


def find_differences(object_with_stats, old_object_with_stats):
    differences = {}
    for key, value in object_with_stats.__dict__.items():
        if(value != old_object_with_stats.__dict__.get(key) and key in {'points', 'fga2', 'fga3', 'fta', 'blocks', 'steals', 'assists', 'offensive_rebounds', 'defensive_rebounds', 'fouls', 'turnovers'}):
            differences[key] = value  
    return differences

def get_differences(teams, old_teams):
    difference_entries = []
    # teams[0].points = 40
    # teams[1].players[0].assists = 30
    # teams[0].players[0].eval = 2030
    for counter, team in enumerate(teams):
        difference_entries.extend(make_difference_entries(team, find_differences(team, old_teams[counter]), team.teamname))
        for counter_player, player in enumerate(team.players):
            difference_entries.extend(make_difference_entries(player, find_differences(player, old_teams[counter].players[counter_player]), f"{player.number} {player.name} {player.surname}"))
    return difference_entries

def save_last_play_to_file(teams, old_teams):
    if(old_teams is None):
        return
    differences = get_differences(teams, old_teams)
    if(differences):
        write_one_line_to_file(f"{path_to_save}/last_play.txt", random.choice(differences))
        # with codecs.open(f"{path_to_save}/last_plays.txt", "w", "utf-8") as myfile:
        #     for difference in differences:
        #         myfile.write(f"{difference}\n")

def get_type_of_random_object():
    probabilities = [1] * 1 + [2] * 3  # 1 - team, 2 - player
    return random.choice(probabilities)

def get_random_player_from_teams(teams, stat_type):
    players_with_weights = []
    for team in teams:
        for player in team.players:
            players_with_weights.extend([player] * (math.ceil(player.minutes / 3)) * math.ceil(getattr(player, stat_type) / 3))
    return random.choice(players_with_weights)

def save_random_stat_to_file():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    object_type = get_type_of_random_object()
    
    if(object_type == 1):
        possible_stats = ['fga2'] * 4 + ['fga3'] * 4 + ['fta'] * 4 + ['blocks'] * 2 + ['steals'] * 5 + ['assists'] * 6 + ['rebounds'] * 4 + ['fouls'] + ['turnovers'] * 6 + ['offensive_rebounds'] * 4 + ['pts_fastb'] * 3 + ['pts_bench'] * 3 + ['pts_paint'] * 3 + ['pts_ch2'] * 3 
        random_possible_stat = random.choice(possible_stats)
        random_stat = f"{getattr(model, f'get_{random_possible_stat}_stat')(teams[0].id, getattr(teams[0], random_possible_stat), teams[0])}, {getattr(model, f'get_{random_possible_stat}_stat')(teams[1].id, getattr(teams[1], random_possible_stat), teams[1])}"
    elif(object_type == 2):
        possible_stats = ['fga2'] * 4 + ['fga3'] * 4 + ['fta'] * 4 + ['blocks'] * 2 + ['steals'] * 5 + ['assists'] * 6 + ['rebounds'] * 4 + ['offensive_rebounds'] * 4 + ['fouls'] + ['turnovers'] * 6
        random_possible_stat = random.choice(possible_stats)
        random_player = get_random_player_from_teams(teams, random_possible_stat)
        random_stat = getattr(model, f'get_{random_possible_stat}_stat')(f'{random_player.short_teamname}: {random_player.number} {random_player.name} {random_player.surname}', getattr(random_player, random_possible_stat), random_player)
    write_one_line_to_file(f"{path_to_save}/random_stat.txt", random_stat)
    make_log(f"Losowa statystyka - {random_stat}")

def infinity_scan(scan_time, function_name, update_log, exception_log):
    while(True):
        try:
            getattr(thismodule, function_name)()
            make_log(f"Uaktualniono {update_log}")
        except Exception:
            make_log(f"Wątek ze {exception_log} natrafił na błąd - {traceback.format_exc()}")
        time.sleep(scan_time)

def scan_fouls(scan_time):
    infinity_scan(scan_time, "save_fouls_to_files", "faule", "skanowaniem fauli")

def scan_players_stats(scan_time):
    infinity_scan(scan_time, "save_players_stats_to_file", "statystyki zawodników", "skanowaniem statystyk zawodników")

def scan_players(scan_time):
    infinity_scan(scan_time, "save_players_to_file", "zawodników", "skanowaniem zawodników")

def scan_points(scan_time):
    infinity_scan(scan_time, "save_team_points_to_files", "punkty drużyn", "skanowaniem punktów drużyn")

def scan_players_oncourt(scan_time):
    infinity_scan(scan_time, "save_players_oncourt_to_file", "zawodników na parkiecie", "skanowaniem zawodników na parkiecie")

def scan_team_stats(scan_time):
    infinity_scan(scan_time, "save_team_stats_to_file", "statystyki drużynowe", "skanowaniem statystyk drużynowych")

def scan_best_players(scan_time):
    infinity_scan(scan_time, "save_best_players_to_files", "najlepszych zawodników", "skanowaniem najlepszych zawodników")

def get_random_stat(scan_time):
    infinity_scan(scan_time, "save_random_stat_to_file", "losową statystykę", "skanowaniem ostatnich zmian")

def scan_quarter(scan_time):
    infinity_scan(scan_time, "save_quarter_to_file", "numer kwarty", "skanowaniem numeru kwarty")

def scan_quarter_time(scan_time):
    infinity_scan(scan_time, "save_time_to_file", "czas kwarty", "skanowaniem czasu kwarty")

def start_thread(method_name, scan_time):
    if(scan_time > 0):
        fouls_thread = threading.Thread(target=method_name, args=(scan_time,))
        fouls_thread.start()
    else:
        make_log(f"{method_name} nie wystartowało")


def scan(scan_times):
    try:
        save_date_to_file(get_date(ET.parse(xml_file_path)))
        save_officials_to_file(get_officials(ET.parse(xml_file_path)))
        save_team_names_to_files(get_teams_from_xml(ET.parse(xml_file_path).getroot()))
        start_thread(scan_fouls, scan_times['fouls'])
        start_thread(scan_players, scan_times['players'])
        start_thread(scan_players_oncourt, scan_times['players_oncourt'])
        start_thread(scan_team_stats, scan_times['teams_stats'])
        start_thread(scan_best_players, scan_times['best_players'])
        start_thread(get_random_stat, scan_times['random_stat'])
        start_thread(scan_players_stats, scan_times['players_stats'])
        start_thread(scan_points, scan_times['team_points'])
        start_thread(scan_quarter, scan_times['period_number'])
        start_thread(scan_quarter_time, scan_times['quarter_time'])
    except FileNotFoundError:
        make_log(f"Plik .xml nie istnieje - {traceback.format_exc()}")
    except KeyError:
        make_log(f"Źle skonfigurowany plik konfiguracyjny 'config.json'- {traceback.format_exc()}") 
    except Exception:
        make_log(f"Coś nie tak - {traceback.format_exc()}")

if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Podaj lokalizację pliku .xml i folderu zapisu")
        sys.exit(1)
    try:
        with codecs.open('config.json') as myfile:
            json_config = json.load(myfile)
        xml_file_path = sys.argv[1]
        path_to_save = sys.argv[2]
        scan_times = json_config['scan_times']
        scan(scan_times)
    except KeyError:
        print(f"Źle skonfigurowany plik konfiguracyjny 'config.json'- {traceback.format_exc()}")
    except ValueError:
        print(f"Niepoprawne okresy odświeżania - {traceback.format_exc()}")
        sys.exit(1)