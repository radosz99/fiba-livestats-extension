import sys
from typing import OrderedDict
import xml.etree.ElementTree as ET


def get_value_from_list_of_tuples_by_key(tuples_list, key_to_find):
    for key, value in tuples_list:
        if(key==key_to_find):
            return value


def get_timeouts_from_current_half(root, team_shortname):
    timeouts = 0
    period = get_value_from_list_of_tuples_by_key(root.find('status').items(), 'period')
    if(int(period) < 3):
        periods = ['1', '2']
    else:
        periods = ['3', '4', '5', '6', '7']

    for quarter_plays in root.findall(f"./plays/period"):
        if(get_value_from_list_of_tuples_by_key(quarter_plays.items(), 'number') in periods):
            for play in quarter_plays.findall('play'):
                if(get_value_from_list_of_tuples_by_key(play.items(), 'action') == "TIMEOUT"):
                    timeouts += 1
    return timeouts
                    


if __name__== "__main__":
    print(get_timeouts_from_current_half(ET.parse(sys.argv[1]).getroot()))