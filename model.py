import copy

class TeamStatisticLine:
    """Klasa reprezentujaca linijke statystyczna druzyny"""
    def __init__(self, fgm, fga,fgm3,fga3,ftm,fta,tp,blk,stl,ast,min,oreb,dreb,treb,pf,tf,to,dq,fgpct,fg3pct,ftpct,teamname,vh, large_lead, lead_time, leads, ties, pts_bench, pts_fastb, pts_paint, pts_ch2, pts_to, short_teamname):
        self.fgm2 = int(fgm) - int(fgm3)
        self.fga2 = int(fga) - int(fga3)
        self.fgm3 = int(fgm3)
        self.fga3 = int(fga3)
        self.fgm = int(fgm)
        self.fga = int(fga)
        self.ftm = int(ftm)
        self.fta = int(fta)
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

    def __eq__(self, other):
        if not isinstance(other, TeamStatisticLine):
            return False
        return self.teamname == other.teamname


class PlayerStatisticLine:
    """Klasa reprezentujaca linijke statystyczna zawodnika"""
    def __init__(self, name, surname, code, fgm=0, fga=0,fgm3=0,fga3=0,ftm=0,fta=0,tp=0,blk=0,stl=0,ast=0,min=0,oreb=0,dreb=0,treb=0,pf=0,tf=0,to=0,dq=0,fgpct=0,fg3pct=0,ftpct=0,gp=0,gs=0,teamname=0,oncourt=0,sec=0,short_teamname=''):
        self.name = name
        self.surname = surname
        self.number = code
        self.fgm = int(fgm)
        self.fga = int(fga)
        self.fgm2 = int(fgm) - int(fgm3)
        self.fga2 = int(fga) - int(fga3)
        self.fgm3 = int(fgm3)
        self.fga3 = int(fga3)
        self.ftm = int(ftm)
        self.fta = int(fta)
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
        if not isinstance(other, PlayerStatisticLine):
            return False
        return self.name == other.name and self.surname == other.surname and self.teamname == other.teamname and self.number == other.number

def make_player_statistic_line(player_stat, player_detail, team):
    if(player_stat is not None):
        player_info = get_dict_from_list_of_tuples(player_stat.items())
    else:
        player_info = dict()
    player_info['teamname'] = team.teamname
    player_info['short_teamname'] = team.id
    for key, value in player_detail.items():
        if(key=='name'):
            if(value=='TEAM'):
                return None
            data = str(value).split(", ")
            player_info['name']=data[1]
            player_info['surname']=data[0]
        if(key=='gp' or key == 'gs' or key == 'code'):
            player_info[key]=value
        if(key=='oncourt'):
            if(value=="Y"):
                player_info[key]=True
            elif(value=="N"):
                player_info[key]=False
    return PlayerStatisticLine(**player_info)

def make_team_statistic_line(team_stat, special_stat, team_detail):
    info = get_dict_from_list_of_tuples(team_stat.items())
    info.update(get_dict_from_list_of_tuples(special_stat.items()))   
    info['teamname'] = get_value_from_list_of_tuples_by_key(team_detail.items(), 'name')
    info['short_teamname'] = get_value_from_list_of_tuples_by_key(team_detail.items(), 'id')
    return TeamStatisticLine(**info)

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
    return root.find('venue/officials').get('text')

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
    if(isinstance(object_with_stats, PlayerStatisticLine)):
        return f"{prefix} - {object_with_stats.points} {get_polish_plural('punkt', 'punkty', 'punktów', object_with_stats.points)}, {object_with_stats.fgm2}/{object_with_stats.fga2} za 2"
    else:
        return f"{prefix} - {object_with_stats.fgm2}/{object_with_stats.fga2} za 2"

def get_fga3_stat(prefix, value, object_with_stats):
    if(isinstance(object_with_stats, PlayerStatisticLine)):
        return f"{prefix} - {object_with_stats.points} {get_polish_plural('punkt', 'punkty', 'punktów', object_with_stats.points)}, {object_with_stats.fgm3}/{object_with_stats.fga3} za 3"
    else:
        return f"{prefix} - {object_with_stats.fgm3}/{object_with_stats.fga3} za 3"

def get_fta_stat(prefix, value, object_with_stats):
    if(isinstance(object_with_stats, PlayerStatisticLine)):
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
