# coding=utf8
import codecs
import time
import threading
import json
import shutil
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
from xml.etree.ElementTree import ParseError
from paramiko.ssh_exception import AuthenticationException, SSHException

from model import get_teams_from_xml, get_fouls, get_officials, get_date, get_value_from_list_of_tuples_by_key, get_object_with_stat_stats_string, get_players_stats_string_to_txt, GraphicEditor, RemoteXML

this_module = sys.modules[__name__]

points_detected = False
probability_random_stat_team, probability_random_stat_player = 1, 3
player_stats_probabilities, team_stats_probabilities = dict(), dict()
logging.getLogger("paramiko").setLevel(logging.WARNING)
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
path_to_save, xml_file_path, resources_path = None, None, None
log = logging.getLogger("basic_logger")
look_for_player_photos = False
fontname = None
server = None
config_json_path = None
server_ip, username, private_key_path, server_path_to_xml, password = None, None, None, None, None

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
        string += f"{player.number} {player.name} {player.surname}\n"
    return string

def get_string_quarter(period):
    try:
        quarter_int = int(period)
    except ValueError:
        overtime = True
        return 'OT'
    if(quarter_int <= 4):
        overtime = False
        return f"{quarter_int}Q"
    else:
        overtime = True
        return f"OT{quarter_int - 4}"

def get_team_stat_string(team):
    string = f"\n{team.defensive_rebounds}\n{team.offensive_rebounds}\n{team.assists}\n{team.steals}\n{team.turnovers}"
    string += f"\n{team.fgm2}/{team.fga2} ({team.fg2_percent}%)"
    string += f"\n{team.fgm3}/{team.fga3} ({team.fg3_percent}%)"
    string += f"\n{team.ftm}/{team.fta} ({team.ft_percent}%)"
    string += f"\n{team.large_lead}\n{team.pts_bench}\n{team.pts_fastb}\n{team.pts_paint}\n{team.pts_ch2}\n{team.pts_to}"
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
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_team_stats.txt", f"{team.teamname}{get_team_stat_string(team)}")

def save_players_stats_to_file():
    root = ET.parse(xml_file_path).getroot()
    teams = get_teams_from_xml(root)
    for counter, team in enumerate(teams):
        graphic_editor = GraphicEditor()
        if(get_status(root)):
            try:
                graphic_editor.edit_photo(counter, resources_path, team, f"{path_to_save}/druzyna_{counter}_players_stats.png", fontname)
                make_info_log(f"Zaktualizowano grafikę ze statystykami zawodników drużyny nr {counter}")
            except OSError:
                make_error_log(f"Wątek ze skanowaniem statystyk nie mógł odnaleźć fontu")
            write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_players_stats.txt", f"{team.teamname}{get_players_stats_string_to_txt(team)}")
        else:
             make_info_log(f"Nie zaktualizowano grafiki ze statystykami zawodników drużyny nr {counter}, czas stoi w miejscu")
        
def get_players_stats_string(players):
    string = ''
    for player in players:
        string += get_object_with_stat_stats_string(player)
    return string

def save_players_to_file():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}.txt", f"{get_players_string(team.players)}")
    make_info_log("Zapisano zawodników")
         
def save_date_to_file(date):
    write_one_line_to_file(f"{path_to_save}/data.txt", date)
    make_info_log("Zapisano datę")

def save_officials_to_file(officials):
    write_one_line_to_file(f"{path_to_save}/officials.txt", officials)
    make_info_log("Zapisano sędziów")

def save_team_names_to_files():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_name.txt", team.teamname)
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_id.txt", team.id)
    make_info_log("Zapisano nazwy oraz id drużyn")

def save_team_points_to_files():
    global points_detected
    root = ET.parse(xml_file_path).getroot()
    points = []
    for linescore in root.findall(f"./team/linescore"):
        points.append(int(get_value_from_list_of_tuples_by_key(linescore.items(), 'score')))
    if(points[0] > 0 or points[1] > 0):
        points_detected = True
    if(points_detected):
        if(points[0] == 0 and points[1] == 0):
            make_info_log("Punkty w xml się wyzerowały, nie zapisuję, zostaje stary wynik")
            return
        else:
            write_one_line_to_file(f"{path_to_save}/druzyna_0_score.txt", str(points[0]))
            write_one_line_to_file(f"{path_to_save}/druzyna_1_score.txt", str(points[1]))
    else:
        write_one_line_to_file(f"{path_to_save}/druzyna_0_score.txt", "0")
        write_one_line_to_file(f"{path_to_save}/druzyna_1_score.txt", "0")

def get_xml_from_server(scan_time):
    while(True):
        try:
            sleeptime = scan_time
            start = time.time()
            if(download_xml_from_server()):

                end = time.time()
                execution_time = end - start
                make_info_log(f"Pobrano plik XML z serwera, wykonano w {round(execution_time, 3)}s")
            else:
                make_warn_log("Plik XML z serwera ma nieprawidłowy format i nie został pobrany")
            sleeptime = 0
        except FileNotFoundError:
            make_error_log(f"Plik XML nie został pobrany z serwera, zła ścieżka do pliku XML na serwerze - {traceback.format_exc()}")
        finally:
            time.sleep(sleeptime)
    

def save_fouls_to_files():
    fouls = get_fouls(ET.parse(xml_file_path).getroot())
    for key, value in fouls.items():
        write_one_line_to_file(f"{path_to_save}/{key}_fouls.txt", str(value))

def save_quarter_to_file():
    root = ET.parse(xml_file_path).getroot()
    period = get_value_from_list_of_tuples_by_key(root.find('status').items(), 'period')
    write_one_line_to_file(f"{path_to_save}/period.txt", get_string_quarter(period))

def save_timeouts_to_file():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    for counter, team in enumerate(teams):
        write_one_line_to_file(f"{path_to_save}/druzyna_{counter}_timeouts.txt", str(team.timeouts))

def get_status(root):
    return False if get_value_from_list_of_tuples_by_key(root.find('status').items(), 'running') == 'F' else True

def save_time_to_file():
    root = ET.parse(xml_file_path).getroot()
    period_time = get_value_from_list_of_tuples_by_key(root.find('status').items(), 'clock')
    
    if(not get_status(root)):
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

def make_info_log(text):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    log.info(f"{dt_string}\t{text}")

def make_warn_log(text):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    log.warning(f"{dt_string}\t{text}")

def make_error_log(text):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    log.error(f"{dt_string}\t{text}") 


    

def get_type_of_random_object():
    probabilities = [1] * probability_random_stat_team + [2] * probability_random_stat_player  # 1 - team, 2 - player
    return random.choice(probabilities)

def get_player_from_teams_depends_on_stat_type(teams, stat_type):
    players_with_weights = []
    for team in teams:
        for player in team.players:
            players_with_weights.extend([player] * (math.ceil(player.minutes / 3)) * math.ceil(getattr(player, stat_type) / 3))
    return random.choice(players_with_weights)

def remove_player_photo():
    try:
        os.remove(f"{path_to_save}/player_photo.png")
        make_info_log("Usunięto zdjęcie zawodnika")
    except FileNotFoundError:
        pass

def update_player_photo(player):
    filename = prepare_photo_file_name(player)
    player_photo_path = f"{resources_path}/photos/{filename}"
    try:
        shutil.copyfile(player_photo_path, f"{path_to_save}/player_photo.png")
        make_info_log(f"Uaktualniono zdjęcie zawodnika, skopiowany plik - \"{player_photo_path}\"")
    except FileNotFoundError:
        remove_player_photo()
        make_warn_log(f"Nieuaktualniono zdjęcia zawodnika, poszukiwany plik do skopiowania nieznaleziony- \"{player_photo_path}\"")
    

def prepare_photo_file_name(player):
    string = f"{remove_accents(player.short_teamname)}_{remove_accents(player.name)}_{remove_accents(player.surname)}.png"
    return string.lower()

def remove_accents(input_text):
    strange='ŮôῡΒძěἊἦëĐᾇόἶἧзвŅῑἼźἓŉἐÿἈΌἢὶЁϋυŕŽŎŃğûλВὦėἜŤŨîᾪĝžἙâᾣÚκὔჯᾏᾢĠфĞὝŲŊŁČῐЙῤŌὭŏყἀхῦЧĎὍОуνἱῺèᾒῘᾘὨШūლἚύсÁóĒἍŷöὄЗὤἥბĔõὅῥŋБщἝξĢюᾫაπჟῸდΓÕűřἅгἰშΨńģὌΥÒᾬÏἴქὀῖὣᾙῶŠὟὁἵÖἕΕῨčᾈķЭτἻůᾕἫжΩᾶŇᾁἣჩαἄἹΖеУŹἃἠᾞåᾄГΠКíōĪὮϊὂᾱიżŦИὙἮὖÛĮἳφᾖἋΎΰῩŚἷРῈĲἁéὃσňİΙῠΚĸὛΪᾝᾯψÄᾭêὠÀღЫĩĈμΆᾌἨÑἑïოĵÃŒŸζჭᾼőΣŻçųøΤΑËņĭῙŘАдὗპŰἤცᾓήἯΐÎეὊὼΘЖᾜὢĚἩħĂыῳὧďТΗἺĬὰὡὬὫÇЩᾧñῢĻᾅÆßшδòÂчῌᾃΉᾑΦÍīМƒÜἒĴἿťᾴĶÊΊȘῃΟúχΔὋŴćŔῴῆЦЮΝΛῪŢὯнῬũãáἽĕᾗნᾳἆᾥйᾡὒსᾎĆрĀüСὕÅýფᾺῲšŵкἎἇὑЛვёἂΏθĘэᾋΧĉᾐĤὐὴιăąäὺÈФĺῇἘſგŜæῼῄĊἏØÉПяწДĿᾮἭĜХῂᾦωთĦлðὩზკίᾂᾆἪпἸиᾠώᾀŪāоÙἉἾρаđἌΞļÔβĖÝᾔĨНŀęᾤÓцЕĽŞὈÞუтΈέıàᾍἛśìŶŬȚĳῧῊᾟάεŖᾨᾉςΡმᾊᾸįᾚὥηᾛġÐὓłγľмþᾹἲἔбċῗჰხοἬŗŐἡὲῷῚΫŭᾩὸùᾷĹēრЯĄὉὪῒᾲΜᾰÌœĥტ'
    ascii_replacements='UoyBdeAieDaoiiZVNiIzeneyAOiiEyyrZONgulVoeETUiOgzEaoUkyjAoGFGYUNLCiIrOOoqaKyCDOOUniOeiIIOSulEySAoEAyooZoibEoornBSEkGYOapzOdGOuraGisPngOYOOIikoioIoSYoiOeEYcAkEtIuiIZOaNaicaaIZEUZaiIaaGPKioIOioaizTIYIyUIifiAYyYSiREIaeosnIIyKkYIIOpAOeoAgYiCmAAINeiojAOYzcAoSZcuoTAEniIRADypUitiiIiIeOoTZIoEIhAYoodTIIIaoOOCSonyKaAsSdoACIaIiFIiMfUeJItaKEISiOuxDOWcRoiTYNLYTONRuaaIeinaaoIoysACRAuSyAypAoswKAayLvEaOtEEAXciHyiiaaayEFliEsgSaOiCAOEPYtDKOIGKiootHLdOzkiaaIPIIooaUaOUAIrAdAKlObEYiINleoOTEKSOTuTEeiaAEsiYUTiyIIaeROAsRmAAiIoiIgDylglMtAieBcihkoIrOieoIYuOouaKerYAOOiaMaIoht'
    translator=str.maketrans(strange,ascii_replacements)
    return input_text.translate(translator)

def get_team_probabilities():
    list_prob = []
    for key, value in team_stats_probabilities.items():
        list_prob.extend([key] * value)
    return list_prob

def get_player_probabilities():
    list_prob = []
    for key, value in player_stats_probabilities.items():
        list_prob.extend([key] * value)
    return list_prob
 
def save_random_stat_to_file():
    teams = get_teams_from_xml(ET.parse(xml_file_path).getroot())
    object_type = get_type_of_random_object()
    if (not get_status(ET.parse(xml_file_path).getroot())):
        make_info_log(f"Losowa statystyka nie zapisana, czas stoi w miejscu")
        return
    if(object_type == 1):
        remove_player_photo()
        random_possible_stat = random.choice(get_team_probabilities())
        random_stat = f"{getattr(model, f'get_{random_possible_stat}_stat')(teams[0].id, getattr(teams[0], random_possible_stat), teams[0])}, {getattr(model, f'get_{random_possible_stat}_stat')(teams[1].id, getattr(teams[1], random_possible_stat), teams[1])}"
    elif(object_type == 2):
        random_possible_stat = random.choice(get_player_probabilities())
        random_player = get_player_from_teams_depends_on_stat_type(teams, random_possible_stat)
        if(look_for_player_photos):
            update_player_photo(random_player)
        random_stat = getattr(model, f'get_{random_possible_stat}_stat')(f'{random_player.short_teamname}: {random_player.number} {random_player.name} {random_player.surname}', getattr(random_player, random_possible_stat), random_player)
    start = time.time()
    write_one_line_to_file(f"{path_to_save}/random_stat.txt", random_stat)
    end = time.time()
    make_info_log(f"Losowa statystyka - {random_stat}")

def infinity_scan(scan_time, function_name, update_log, exception_log):
    while(True):
        try:
            start = time.time()
            getattr(this_module, function_name)()
            end = time.time()
            execution_time = end - start
            make_info_log(f"Uaktualniono {update_log}, wykonano w {round(execution_time, 3)}s")
        except ParseError:
            make_warn_log(f"Wątek ze skanowaniem {exception_log} nie mógł odczytać pliku XML")
            execution_time = 0
        except Exception:
            make_error_log(f"Wątek ze skanowaniem {exception_log} natrafił na błąd - {traceback.format_exc()}")
            execution_time = 0
        sleeptime = scan_time - execution_time if (scan_time - execution_time) > 0 else 0
        time.sleep(sleeptime)

def scan_fouls(scan_time):
    infinity_scan(scan_time, "save_fouls_to_files", "faule", "fauli")

def scan_players_stats(scan_time):
    infinity_scan(scan_time, "save_players_stats_to_file", "statystyki zawodników", "statystyk zawodników")

def scan_points(scan_time):
    infinity_scan(scan_time, "save_team_points_to_files", "punkty drużyn", "punktów drużyn")

def scan_players_oncourt(scan_time):
    infinity_scan(scan_time, "save_players_oncourt_to_file", "zawodników na parkiecie", "zawodników na parkiecie")

def scan_team_stats(scan_time):
    infinity_scan(scan_time, "save_team_stats_to_file", "statystyki drużynowe", "statystyk drużynowych")

def scan_best_players(scan_time):
    infinity_scan(scan_time, "save_best_players_to_files", "najlepszych zawodników", "najlepszych zawodników")

def get_random_stat(scan_time):
    infinity_scan(scan_time, "save_random_stat_to_file", "losową statystykę", "ostatnich zmian")

def scan_quarter(scan_time):
    infinity_scan(scan_time, "save_quarter_to_file", "numer kwarty", "numeru kwarty")

def scan_timeouts(scan_time):
    infinity_scan(scan_time, "save_timeouts_to_file", "numer kwarty", "numeru kwarty")

def scan_quarter_time(scan_time):
    infinity_scan(scan_time, "save_time_to_file", "czas kwarty", "czasu kwarty")

def start_thread(method_name, scan_time):
    if(scan_time > 0):
        fouls_thread = threading.Thread(target=method_name, args=(scan_time,))
        fouls_thread.start()
    else:
        make_warn_log(f"{method_name} nie wystartowało, czas z 'config.json' nie jest większy od 0")

def download_xml_from_server():
    server.download_xml_from_server("temp.xml")
    try:
        ET.parse("temp.xml")
        shutil.copy("temp.xml", xml_file_path)
        os.remove("temp.xml")
        return True
    except:
        os.remove("temp.xml")
        return False
    

def init_ssh_session_with_server():
    make_info_log("Pobieranie pliku XML z serwera")
    if(server.init_ssh_session()):
        if(download_xml_from_server()):
            make_info_log("Pobrano plik XML z serwera")
        else:
            make_warn_log("Plik XML z serwera ma nieprawidłowy format i nie został pobrany")
        return True
    else:
        return False

def init_ssh_session():
    try:
        if(not init_ssh_session_with_server()):
            make_error_log("Nie powiodła się próba zalogowania ani przez hasło ani przez klucz")
            sys.exit(1)
            
    except AuthenticationException:
        make_error_log(f"Plik XML nie został pobrany z serwera, prawdopodobnie zła nazwa użytkownika bądź klucz nierozpoznawany przez serwer - {traceback.format_exc()}")
        sys.exit(1)
    except SSHException:
        make_error_log(f"Plik XML nie został pobrany z serwera, prawdopodobnie zły format klucza - {traceback.format_exc()}")
        sys.exit(1)
    except FileNotFoundError:
        make_error_log(f"Plik XML nie został pobrany z serwera, zła ścieżka do klucza bądź do pliku XML na serwerze - {traceback.format_exc()}")
        sys.exit(1)
    except TimeoutError:
        make_error_log(f"Plik XML nie został pobrany z serwera, prawdopodobnie zły adres IP - {traceback.format_exc()}")
        sys.exit(1)
 
def save_basic_info_to_files():
    while(True):
        try:    
            save_date_to_file(get_date(ET.parse(xml_file_path)))
            save_officials_to_file(get_officials(ET.parse(xml_file_path)))
            save_team_names_to_files()
            save_players_to_file()
            break
        except Exception:
            make_error_log(f"Plik xml jest niewłaściwie sformatowany, nie można pobrać daty, sędziów, drużyn i zawodników! - {traceback.format_exc()}")
            time.sleep(2)

def scan(scan_times):
    global server
    server = RemoteXML(server_ip, username, private_key_path, server_path_to_xml, password)
    try:
        if(remote_xml):
            init_ssh_session()
            start_thread(get_xml_from_server, 2)
        save_basic_info_to_files()
        start_thread(scan_fouls, scan_times['fouls'])
        start_thread(scan_players_oncourt, scan_times['players_oncourt'])
        start_thread(scan_team_stats, scan_times['teams_stats'])
        start_thread(scan_best_players, scan_times['best_players'])
        start_thread(get_random_stat, scan_times['random_stat'])
        start_thread(scan_players_stats, scan_times['players_stats'])
        start_thread(scan_points, scan_times['team_points'])
        start_thread(scan_quarter, scan_times['period_number'])
        start_thread(scan_quarter_time, scan_times['quarter_time'])
        start_thread(scan_timeouts, scan_times['timeouts'])
    except FileNotFoundError:
        make_error_log(f"Plik {xml_file_path} nie istnieje - {traceback.format_exc()}")
    except KeyError:
        make_error_log(f"Źle skonfigurowany plik konfiguracyjny 'config.json'- {traceback.format_exc()}") 
    except Exception:
        make_error_log(f"Coś nie tak - {traceback.format_exc()}")

def parse_config_json():
    with codecs.open(config_json_path) as myfile:
        return json.load(myfile)

def get_path_from_config_json(value):
    json_config = parse_config_json()
    try:
        return json_config[value]
    except:
        make_error_log(f"Nieprawidłowe nazwy ścieżek w pliku konfiguracyjnym 'config.json' - {traceback.format_exc()}")
        raise KeyError

def check_if_look_for_photos():
    json_config = parse_config_json()
    try:
        return bool(json_config['look_for_player_photos'])
    except (KeyError, TypeError):
        return False
    

def check_if_files_exist(files):
    for file_to_check in files:
        if(not os.path.exists(file_to_check)):
            return False
    return True

def check_if_file_exists(file_to_check):
    if(os.path.exists(file_to_check)):
        return True
    else:
        return False

def get_probabilities_of_object_with_stats_from_config_json():
    config_json = parse_config_json()
    return config_json["probabilities"]["team"], config_json["probabilities"]["player"]

def get_probabilities_of_stats_from_config_json():
    config_json = parse_config_json()
    return config_json["probabilities"]["player_stats"], config_json["probabilities"]["team_stats"]

def check_if_login_by_private_key(server_info):
    global private_key_path
    try:
        private_key_path = server_info['private_key_path']
        return check_if_file_exists(private_key_path)
    except KeyError:
        return False
    
def check_if_xml_file_from_server():
    global server_ip, username, server_path_to_xml, password
    config_json = parse_config_json()
    try:
        server_info = config_json['server']
        make_info_log("Wybrano pobieranie pliku XML z serwera")
    except:
        make_error_log("Brakuje parametru 'server' w pliku 'config.json', XML będzie pobierany z lokalnej lokalizacji")
        return False

    try:
        server_ip, username, server_path_to_xml = server_info['ip'], server_info['username'], server_info['xml_path']   
    except KeyError:
        make_error_log("Brakuje którego z parametrów w 'config.json' - 'ip', 'username' albo 'xml_path'")
        sys.exit(1)
    
    if(check_if_login_by_private_key(server_info)):
        make_info_log(f"Wybrano logowanie przez klucz prywatny z lokalizacji {private_key_path}")
        return True
    else:
        try:
            password = server_info['password']
            make_info_log(f"Wybrano logowanie przez hasło")
            return True
        except KeyError:
            make_error_log(f"Nie będzie można pobrać pliku z serwera, dodaj parametr 'private_key_path' bądź 'password'")
            sys.exit(1)


def set_probabilities():
    global probability_random_stat_player, probability_random_stat_team, player_stats_probabilities, team_stats_probabilities
    probability_random_stat_team, probability_random_stat_player = get_probabilities_of_object_with_stats_from_config_json()
    player_stats_probabilities, team_stats_probabilities = get_probabilities_of_stats_from_config_json()

def set_fontname():
    global fontname
    try:
        fontname = parse_config_json()['fontname']
    except KeyError:
        fontname = None

    
def get_paths_from_config_json():
    global xml_file_path, path_to_save, resources_path
    try:
        xml_file_path = get_path_from_config_json('local_xml_path')
        path_to_save = get_path_from_config_json('save_directory_path')
        resources_path = get_path_from_config_json('resources_path')
        if(not check_if_file_exists(resources_path)):
            make_warn_log(f"Ścieżka do 'resources' nie istnieje ({resources_path}), nie będzie możliwe utworzenie grafik oraz kopii zdjęć zawodników")
    except KeyError:
        make_error_log(f"Złe nazwy ścieżek w pliku 'config.json', brakuje 'local_xml_path' albo 'save_directory_path'")
        sys.exit(1)
    
    if(check_if_file_exists(path_to_save)):
        make_info_log("Ścieżka do zapisu pobrana z config.json istnieje!")
        if(not check_if_file_exists(xml_file_path)):
            if(remote_xml):
                make_info_log("Plik XML będzie pobierany z serwera!")
            else:
                make_error_log("Nie wybrano pobierania pliku XML z serwera, a plik zawarty w 'local_xml_path' nie istnieje!")
                sys.exit(1)
    else:
        make_warn_log("Ścieżka do zapisu pobrana z config.json NIE ISTNIEJE!")
        os.mkdir(path_to_save)
        make_info_log(f"Utworzono folder w którym będą zapisywane pliki")

def get_scan_times():
    return parse_config_json()['scan_times']

def parametrize_scanner_by_variables_from_config_json():
    get_paths_from_config_json()
    set_fontname()

    try:
        set_probabilities()
    except KeyError:
        make_error_log("Źle ustawione prawdopobieństwa w pliku 'config.json'")
        sys.exit(1)

if __name__ == "__main__":
    try:
        config_json_path = sys.argv[1]
    except IndexError:
        print("Podaj pełną ścieżkę do pliku 'config.json'")
        sys.exit(1)
    if(not check_if_file_exists(config_json_path)):
        print(f"Plik {config_json_path} nie istnieje")
        sys.exit(1)

    remote_xml = check_if_xml_file_from_server()
    look_for_player_photos = check_if_look_for_photos()
    parametrize_scanner_by_variables_from_config_json()

    try:
        scan_times = get_scan_times()
    except KeyError:
        print("Brakuje parametru 'scan_times' w pliku 'config.json'")
        sys.exit(1)
    
    scan(scan_times)