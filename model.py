class TeamStatisticLine:
    """Klasa reprezentujaca linijke statystyczna druzyny"""
    def __init__(self, fgm, fga,fgm3,fga3,ftm,fta,tp,blk,stl,ast,min,oreb,dreb,treb,pf,tf,to,dq,fgpct,fg3pct,ftpct,teamname,vh, large_lead, lead_time, leads, ties, pts_bench, pts_fastb, pts_paint, pts_ch2, pts_to):
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
        self.fouls = int(pf)
        self.tf = int(tf)
        self.turnovers = int(to)
        self.disq = int(dq)
        self.teamname = teamname
        self.large_lead = int(large_lead)
        self.pts_bench = pts_bench
        self.pts_fastb = pts_fastb
        self.pts_paint = pts_paint
        self.pts_ch2 = pts_ch2
        self.pts_to = pts_to

    def __repr__(self):
        return f'\nPoints - {self.points}, Team - {self.teamname}'


class PlayerStatisticLine:
    """Klasa reprezentujaca linijke statystyczna zawodnika"""
    def __init__(self, name, surname, code, fgm, fga,fgm3,fga3,ftm,fta,tp,blk,stl,ast,min,oreb,dreb,treb,pf,tf,to,dq,fgpct,fg3pct,ftpct,gp,gs,teamname,oncourt,sec=0):
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
        self.eval = self.points + self.rebounds + self.steals + self.blocks + self.assists - self.turnovers - (self.fga - self.fgm) - (self.fta - self.ftm)
        self.oncourt = oncourt
        
    def __repr__(self):
        return f'{self.name}, {self.surname}, {self.number}, {self.teamname}, {self.oncourt}'

def make_player_statistic_line(player_stat, player_detail, teamname):
    info = get_dict_from_list_of_tuples(player_stat.items())
    info['teamname'] = teamname
    for key, value in player_detail.items():
        if(key=='name'):
            if(value=='TEAM'):
                return None
            data = str(value).split(", ")
            info['name']=data[1]
            info['surname']=data[0]
        if(key=='gp' or key == 'gs' or key == 'code'):
            info[key]=value
        if(key=='oncourt'):
            if(value=="Y"):
                info[key]=True
            elif(value=="N"):
                info[key]=False
    return PlayerStatisticLine(**info)

def make_team_statistic_line(team_stat, special_stat, team_detail):
    info = get_dict_from_list_of_tuples(team_stat.items())
    info.update(get_dict_from_list_of_tuples(special_stat.items()))   
    info['teamname'] = get_value_from_list_of_tuples_by_key(team_detail.items(), 'name')
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

def get_fouls(root):
    period = root.find('status').get('period')
    fouls = []
    for info in root.findall(f"./team/totals/statsbyprd"):
        if(period == info.get('prd')):
            foul_amount = int(info.get('pf'))
            if(foul_amount > 5):
                foul_amount = 5
            fouls.append(foul_amount)
    return fouls[0], fouls[1]


def get_informations_from_root(root):
    players,teams = [],[]
    
    date = f"{root.find('venue').get('date')} {root.find('venue').get('start')}"
    for team_xml in root.findall("./team"):
        team = make_team_statistic_line(team_xml.find("./totals/stats"),team_xml.find("./totals/special"), team_xml)
        teams.append(team)
        for player_info in team_xml.findall("player"):
            player = make_player_statistic_line(player_info.find('stats'), player_info, team.teamname)
            if(player is not None):
                players.append(player)
    return players, teams, date