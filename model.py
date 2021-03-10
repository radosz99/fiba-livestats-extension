# coding=utf8
import os
import sys
import copy
import paramiko
import logging
from PIL import Image, ImageFont, ImageDraw, ImageFilter 
from paramiko.ssh_exception import AuthenticationException, SSHException

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger("paramiko_logger")


class Team:
    """Klasa reprezentujaca linijke statystyczna druzyny"""
    def __init__(self, fgm, fga,fgm3,fga3,ftm,fta,tp,blk,stl,ast,min,oreb,dreb,treb,pf,tf,to,dq,fgpct,fg3pct,ftpct,teamname,vh, large_lead, lead_time, leads, ties, pts_bench, pts_fastb, pts_paint, pts_ch2, pts_to, short_teamname):
        self.fgm2 = int(fgm) - int(fgm3)
        self.fga2 = int(fga) - int(fga3)
        self.fg2_percent = f"{round(self.fgm2/self.fga2 * 100, 1)}" if self.fga2 != 0 else "0.0"
        self.fgm3 = int(fgm3)
        self.fga3 = int(fga3)
        self.fg3_percent = f"{round(self.fgm3/self.fga3 * 100, 1)}" if self.fga3 != 0 else "0.0"
        self.fgm = int(fgm)
        self.fga = int(fga)
        self.fg_percent = f"{round(self.fgm/self.fga * 100, 1)}" if self.fga != 0 else "0.0"
        self.ftm = int(ftm)
        self.fta = int(fta)
        self.ft_percent = f"{round(self.ftm/self.fta * 100, 1)}" if self.fta != 0 else "0.0"
        self.points = int(tp)
        self.blocks = int(blk)
        self.steals = int(stl)
        self.assists = int(ast)
        self.minutes = int(min)
        self.offensive_rebounds = int(oreb)
        self.defensive_rebounds = int(dreb)
        self.rebounds = self.defensive_rebounds + self.offensive_rebounds
        self.fouls = int(pf)
        self.tf = int(tf)
        self.turnovers = int(to)
        self.disq = int(dq)
        self.teamname = teamname
        self.large_lead = int(large_lead)
        self.pts_bench = int(pts_bench)
        self.pts_fastb = int(pts_fastb)
        self.pts_paint = int(pts_paint)
        self.pts_ch2 = int(pts_ch2)
        self.pts_to = int(pts_to)
        self.players = []
        self.id = short_teamname

    def __repr__(self):
        return f'\nPoints - {self.points}, Team - {self.teamname}, Players - {self.players}'

    def set_team_stats(self, oreb, dreb, treb, pf, tf, to, dq, code):
        self.team_oreb = oreb
        self.team_dreb = dreb
        self.team_treb = treb
        self.team_to = to

    def __eq__(self, other):
        if not isinstance(other, Team):
            return False
        return self.teamname == other.teamname


class Player:
    """Klasa reprezentujaca linijke statystyczna zawodnika"""
    def __init__(self, name, surname, code, fgm=0, fga=0,fgm3=0,fga3=0,ftm=0,fta=0,tp=0,blk=0,stl=0,ast=0,min=0,oreb=0,dreb=0,treb=0,pf=0,tf=0,to=0,dq=0,fgpct=0,fg3pct=0,ftpct=0,gp=0,gs=0,teamname=0,oncourt=0,sec=0,short_teamname=''):
        self.name = name
        self.surname = surname
        self.number = code
        self.length_of_prefix = len(f"{name}{surname}{code}")
        # self.prefix = (f" {code}" if len(str(code))==1 else f"{code}") + f" {name} {surname}"
        self.fullname = f"{name} {surname}"
        self.fgm2 = int(fgm) - int(fgm3)
        self.fga2 = int(fga) - int(fga3)
        self.fg2_percent = f"{round(self.fgm2/self.fga2 * 100, 1)}" if self.fga2 != 0 else "0.0"
        self.fgm3 = int(fgm3)
        self.fga3 = int(fga3)
        self.fg3_percent = f"{round(self.fgm3/self.fga3 * 100, 1)}" if self.fga3 != 0 else "0.0"
        self.fgm = int(fgm)
        self.fga = int(fga)
        self.fg_percent = f"{round(self.fgm/self.fga * 100, 1)}" if self.fga != 0 else "0.0"
        self.ftm = int(ftm)
        self.fta = int(fta)
        self.ft_percent = f"{round(self.ftm/self.fta * 100, 1)}" if self.fta != 0 else "0.0"
        self.points = int(tp)
        self.blocks = int(blk)
        self.steals = int(stl)
        self.assists = int(ast)
        self.minutes = int(min)
        self.offensive_rebounds = int(oreb)
        self.defensive_rebounds = int(dreb)
        self.rebounds = self.offensive_rebounds + self.defensive_rebounds
        self.fouls = int(pf)
        self.tf = int(tf)
        self.turnovers = int(to)
        self.disq = int(dq)
        self.gp=gp
        self.gs=gs
        self.teamname = teamname
        self.short_teamname = short_teamname
        self.eval = self.points + self.rebounds + self.steals + self.blocks + self.assists - self.turnovers - (self.fga - self.fgm) - (self.fta - self.ftm)
        self.oncourt = oncourt
        
    def __repr__(self):
        return f'{self.name}, {self.surname}, {self.number}, {self.teamname}, {self.oncourt}'

    def __eq__(self, other):
        if not isinstance(other, Player):
            return False
        return self.name == other.name and self.surname == other.surname and self.teamname == other.teamname and self.number == other.number

class RemoteXML():
    def __init__(self, server_ip, username, private_key_path, server_path_to_xml, password):
        self.server_ip = server_ip
        self.username = username
        self.private_key_path = private_key_path
        self.server_path_to_xml = server_path_to_xml
        self.password = password

    def init_ssh_session(self):
        self.ssh = paramiko.SSHClient() 
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            k = paramiko.RSAKey.from_private_key_file(filename=self.private_key_path)
            self.ssh.connect(hostname=self.server_ip, username=self.username, pkey=k)
        except (AuthenticationException, FileNotFoundError, SSHException):
            log.warning("Plik z kluczem nie znaleziony bądź nieprawidłowy, próba logowania przez hasło")
            try:
                self.ssh.connect(hostname=self.server_ip, username=self.username, password=self.password)
                log.info("Udało się zalogować za pomocą hasła")
            except AuthenticationException:
                log.error("Hasło z 'config.json' jest nieprawidłowe!")
                return False
        self.sftp = self.ssh.open_sftp()
        return True

    def download_xml_from_server(self, local_save_path):
        self.sftp.get(self.server_path_to_xml, local_save_path)

    def close_ssh_session(self):
        self.sftp.close()
        self.ssh.close()


def make_player_statistic_line(player_stat, player_detail, team):
    if(player_stat is not None):
        player_info = get_dict_from_list_of_tuples(player_stat.items())
    else:
        player_info = dict()
    for key, value in player_detail.items():
        if(key=='name'):
            if(value=='TEAM'):
                team.set_team_stats(**player_info)
                return None
            data = str(value).replace(' ', '')
            data = data.split(",")
            player_info['name']=data[1]
            player_info['surname']=data[0]
        if(key=='gp' or key == 'gs' or key == 'code'):
            player_info[key]=value
        if(key=='oncourt'):
            if(value=="Y"):
                player_info[key]=True
            elif(value=="N"):
                player_info[key]=False
    player_info['teamname'] = team.teamname
    player_info['short_teamname'] = team.id
    return Player(**player_info)

def make_team_statistic_line(team_stat, special_stat, team_detail):
    info = get_dict_from_list_of_tuples(team_stat.items())
    info.update(get_dict_from_list_of_tuples(special_stat.items()))   
    info['teamname'] = get_value_from_list_of_tuples_by_key(team_detail.items(), 'name')
    info['short_teamname'] = get_value_from_list_of_tuples_by_key(team_detail.items(), 'id')
    return Team(**info)

def get_value_from_list_of_tuples_by_key(tuples_list, key_to_find):
    for key, value in tuples_list:
        if(key==key_to_find):
            return value

def get_dict_from_list_of_tuples(tuples_list):
    info = dict()
    for key, value in tuples_list:
            info[key]=value
    return info

def get_fouls_from_period(root, period):
    if(period < 1):
        return
    fouls = {}
    for counter, totals in enumerate(root.findall(f"./team/totals")):
        for statsbyprd in totals.findall(f"statsbyprd"):
            if(str(period) == statsbyprd.get('prd')):
                foul_amount = int(statsbyprd.get('pf'))
                if(foul_amount > 5):
                    foul_amount = 5
                fouls[f"druzyna_{counter}"] = foul_amount
    return fouls
        

def get_fouls(root):
    period = int(root.find('status').get('period'))
    fouls = get_fouls_from_period(root, period)
    if(not fouls):
        fouls = get_fouls_from_period(root, period - 1)
    if(not fouls):
        fouls = dict()
        fouls[f"druzyna_0"] = 0
        fouls[f"druzyna_1"] = 0
    return fouls

def get_officials(root):
    officials_string = ""
    officials_single = root.find('venue/officials').get('text').split(', ')
    for official_single in officials_single:
        officials_string += f"{official_single}\n"
    return officials_string 

def get_date(root):
    return f"{root.find('venue').get('date')} {root.find('venue').get('start')}"

def get_teams_from_xml(root):
    players,teams = [],[]
    
    for team_xml in root.findall("./team"):
        team = make_team_statistic_line(team_xml.find("./totals/stats"),team_xml.find("./totals/special"), team_xml)
        for player_info in team_xml.findall("player"):
            player = make_player_statistic_line(player_info.find('stats'), player_info, team)
            if(player is not None):
                players.append(player)
    
        team.players = copy.deepcopy(players)
        players = []
        teams.append(team)
    return teams


def get_points_stat(prefix, value, object_with_stats):
    return f"{prefix} - {object_with_stats.points} {get_polish_plural('punkt', 'punkty', 'punktów', object_with_stats.points)}, {object_with_stats.fgm3}/{object_with_stats.fga3} za 3, {object_with_stats.fgm2}/{object_with_stats.fga2} za 2, {object_with_stats.ftm}/{object_with_stats.fta} za 1"

def get_fga2_stat(prefix, value, object_with_stats):
    if(isinstance(object_with_stats, Player)):
        return f"{prefix} - {object_with_stats.points} {get_polish_plural('punkt', 'punkty', 'punktów', object_with_stats.points)}, {object_with_stats.fgm2}/{object_with_stats.fga2} za 2"
    else:
        return f"{prefix} - {object_with_stats.fgm2}/{object_with_stats.fga2} za 2"

def get_fga3_stat(prefix, value, object_with_stats):
    if(isinstance(object_with_stats, Player)):
        return f"{prefix} - {object_with_stats.points} {get_polish_plural('punkt', 'punkty', 'punktów', object_with_stats.points)}, {object_with_stats.fgm3}/{object_with_stats.fga3} za 3"
    else:
        return f"{prefix} - {object_with_stats.fgm3}/{object_with_stats.fga3} za 3"

def get_fta_stat(prefix, value, object_with_stats):
    if(isinstance(object_with_stats, Player)):
        return f"{prefix} - {object_with_stats.points} {get_polish_plural('punkt', 'punkty', 'punktów', object_with_stats.points)}, {object_with_stats.ftm}/{object_with_stats.fta} za 1"
    else:
        return f"{prefix} - {object_with_stats.ftm}/{object_with_stats.fta} za 1"

def get_blocks_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('blok', 'bloki', 'bloków', value)}"

def get_pts_fastb_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('punkt', 'punkty', 'punktów', value)} z kontry"

def get_pts_bench_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('punkt', 'punkty', 'punktów', value)} ławki"

def get_pts_paint_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('punkt', 'punkty', 'punktów', value)} z pomalowanego"

def get_pts_ch2_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('punkt', 'punkty', 'punktów', value)} drugiej szansy"

def get_steals_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('przechwyt', 'przechwyty', 'przechwytów', value)}"

def get_assists_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('asysta', 'asysty', 'asyst', value)}"

def get_offensive_rebounds_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('zbiórka', 'zbiórki', 'zbiórek', value)} w ataku"

def get_defensive_rebounds_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('zbiórka', 'zbiórki', 'zbiórek', value)} w obronie"

def get_rebounds_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('zbiórka', 'zbiórki', 'zbiórek', value)}"

def get_fouls_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('faul', 'faule', 'fauli', value)}"

def get_turnovers_stat(prefix, value, object_with_stats):
    return f"{prefix} - {value} {get_polish_plural('strata', 'straty', 'strat', value)}"

def get_polish_plural(singularNominativ, pluralNominativ, pluralGenitive, value):
    if (value == 1):
        return singularNominativ
    elif (value % 10 >= 2 and value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20)):
        return pluralNominativ
    else:
        return pluralGenitive

def get_fg_percent_string(percent):
    if(len(percent)==3):
        return f"  {percent}"
    elif(len(percent)==4):
        return f" {percent}" 
    elif(len(percent)==5):
        return percent


def get_fg_string(attempts, made, percent):
    space_shift = '   '
    string = ''
    if(attempts != 0):
        if(len(str(made))==1):
            player_fgm2 = f" {made}"
        else:
            player_fgm2 = made
        if(len(str(attempts))==1):
            player_fga2 = f"{attempts} "
        else:
            player_fga2 = attempts
        string += f"{space_shift}{player_fgm2}/{player_fga2}"
        string += f"{space_shift}{get_fg_percent_string(percent)}%"
    else:
        string += f"{space_shift}     {space_shift}  0.0%"
    return string

def get_value_on_3_position(value):
    if(len(value)==1):
        return f" {value} "
    elif(len(value)==2):
        return f"{value} "
    elif(len(value)==3):
        return f"{value}"

def get_object_with_stat_stats_string(object_with_stat):
    string = ''
    space_shift = '   '
    string += get_value_on_3_position(str(object_with_stat.points))
    string += get_fg_string(object_with_stat.fga2, object_with_stat.fgm2, object_with_stat.fg2_percent)
    string += get_fg_string(object_with_stat.fga3, object_with_stat.fgm3, object_with_stat.fg3_percent)
    string += get_fg_string(object_with_stat.fta, object_with_stat.ftm, object_with_stat.ft_percent)
    for value in [object_with_stat.offensive_rebounds, object_with_stat.defensive_rebounds, object_with_stat.rebounds, object_with_stat.assists, object_with_stat.fouls, object_with_stat.turnovers, object_with_stat.steals, object_with_stat.blocks]:
        string += get_value_if_not_equals_to_zero(value)
    if(isinstance(object_with_stat, Player)):
        string += f"{space_shift}{object_with_stat.eval}"
    return string

def get_team_stats_string(team):
    return ' ' * 54 + f"{get_value_if_not_equals_to_zero(team.team_oreb)}{get_value_if_not_equals_to_zero(team.team_dreb)}{get_value_if_not_equals_to_zero(team.team_treb)}" + ' ' * 12 + get_value_with_tab_if_not_equals_to_zero(team.team_to)

def get_players_stats_string_to_txt(team):
    string = ''
    max_prefix_length = max(player.length_of_prefix for player in team.players)
    for player in team.players:  
        string += f"\n{player.number} {player.name} {player.surname}" + " " * (max_prefix_length - player.length_of_prefix) 
        string += f"\t{player.points}\t{player.minutes}"
        string += get_object_with_stat_string(player)
        string += f"\t{player.eval}"
    string += f"\nDrużynowe\t\t\t\t\t\t\t\t\t\t\t{get_value_with_tab_if_not_equals_to_zero(team.team_oreb)}{get_value_with_tab_if_not_equals_to_zero(team.team_dreb)}{get_value_with_tab_if_not_equals_to_zero(team.team_treb)}\t\t\t{get_value_with_tab_if_not_equals_to_zero(team.team_to)}"
    string += "\nSuma\t"
    return string

def get_object_with_stat_string(object_with_stat):
    string = ''
    if(object_with_stat.fga2 != 0):
        string += f"\t{object_with_stat.fgm2}/{object_with_stat.fga2}"
        string += f"\t{object_with_stat.fg2_percent}%"
    else:
        string += f"\t\t0.0%"

    if(object_with_stat.fga3 != 0):
        string += f"\t{object_with_stat.fgm3}/{object_with_stat.fga3}"
        string += f"\t{object_with_stat.fg3_percent}%"
    else:
        string += f"\t\t0.0%"

    if(object_with_stat.fga != 0):
        string += f"\t{object_with_stat.fgm}/{object_with_stat.fga}"
        string += f"\t{object_with_stat.fg_percent}%"
    else:
        string += f"\t\t0.0%"

    if(object_with_stat.fta !=0):
        string += f"\t{object_with_stat.ftm}/{object_with_stat.fta}"
        string += f"\t{object_with_stat.ft_percent}%"
    else:
        string += f"\t\t0.0%"
        
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.offensive_rebounds)
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.defensive_rebounds)
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.rebounds)
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.assists)
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.fouls)
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.turnovers)
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.steals)
    string += get_value_with_tab_if_not_equals_to_zero(object_with_stat.blocks)
    return string

def get_value_if_not_equals_to_zero(value):
    space_shift = '   '
    if(value != 0):
        return f"{space_shift}{value}" + ' ' * (2 - len(str(value)))
    else:
        return f"{space_shift}  "

def get_value_with_tab_if_not_equals_to_zero(value):
    if(value != 0):
        return f"\t{value}"
    else:
        return f"\t"

class GraphicEditor():
    def __init___(self):
        pass
    
    def edit_photo(self, team_counter, resources_path, team, filename_to_save, fontname):
        my_image = Image.open(f"{resources_path}\\templates\\player_stats.png")
        font_fullname = ImageFont.truetype(f"{resources_path}\\fonts\\{fontname}.ttf", 24)
        font_stats_bold = ImageFont.truetype(f"{resources_path}\\fonts\\{fontname}.ttf", 22)
        team_font = ImageFont.truetype(f"{resources_path}\\fonts\\{fontname}.ttf", 80)
        image_editable = ImageDraw.Draw(my_image)
        try:
            team_logo = Image.open(f"{resources_path}\\photos\\druzyna_{team_counter}_logo.png")
            team_logo.thumbnail((335,335), Image.ANTIALIAS)
            my_image.paste(team_logo)
        except FileNotFoundError:
            print(f"Wątek ze skanowaniem statystyk nie mógł odnaleźć loga drużyny {team.teamname}, powinno znajdować się w katalogu 'resources\\photos\' w pliku 'druzyna_{team_counter}_logo.png'")
        image_editable.text((400, 120), team.teamname, (255, 255, 255), font=team_font)
        shift = 45
        shift_common = 4
        shift_fg = 6
        stats_string = f"PKT{' ' * shift_common}2P{' ' * shift_fg}2P%{' ' * shift_fg}3P{' ' * shift_fg}3P%{' ' * shift_fg}1P{' ' * shift_fg}1P%     ZA   ZO   ZS   A    F    S    P    B   EVAL"
        
        image_editable.text((550, 330), stats_string, (255, 255, 255), font=font_stats_bold)

        image_editable.line([(530,330), (530, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(605,330), (605, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(705,330), (705, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(830,330), (830, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(925,330), (925, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1050,330), (1050, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1145,330), (1145, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1270,330), (1270, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1330,330), (1330, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1395,330), (1395, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1460,330), (1460, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1525,330), (1525, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1590,330), (1590, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1655, 330), (1655, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1720, 330), (1720, 995)], fill =(0, 0, 0), width = 2)
        image_editable.line([(1785, 330), (1785, 995)], fill =(0, 0, 0), width = 2)
        

        counter = 0
        for player in team.players:
            number = player.number if len(player.number)==2 else f" {player.number}"
            image_editable.text((100, 380 + shift * counter), number, (255, 255, 255), font=font_fullname)
            image_editable.text((160, 380 + shift * counter), player.fullname, (0, 0, 0), font=font_fullname)
            image_editable.text((550, 380 + shift * counter), get_object_with_stat_stats_string(player), (0, 0, 0), font=font_stats_bold)
            image_editable.line([(100, 370 + shift * counter), (1850, 370 + shift * counter)], fill =(0, 0, 0), width = 2)
            counter += 1
        image_editable.text((160, 380 + shift * counter), "Drużynowe", (0, 0, 0), font=font_fullname)
        image_editable.text((550, 380 + shift * counter), get_team_stats_string(team), (0, 0, 0), font=font_stats_bold)
        image_editable.line([(100, 370 + shift * counter), (1850, 370 + shift * counter)], fill =(0, 0, 0), width = 4)
        counter += 1
        image_editable.text((160, 380 + shift * counter), "Suma", (0, 0, 0), font=font_fullname)
        image_editable.text((550, 380 + shift * counter), get_object_with_stat_stats_string(team), (0, 0, 0), font=font_stats_bold)
        image_editable.line([(100, 370 + shift * counter), (1850, 370 + shift * counter)], fill =(0, 0, 0), width = 5)
        my_image.save(filename_to_save)

