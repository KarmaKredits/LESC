from googleSheets import getMatches
from redisDB import redisDB

# def s():


if __name__ == '__main__':
    rc=redisDB()
    db = rc.getValue('lesc_db')
    matches = getMatches(db)
    # print(matches)
    # ['Home Team', '', 'Away Team', 'Day', 'Date', 'Time', 'Commentating ', 'Result']
    # ['Nked Dommer-nuts', 'v', 'JustZees League ', 'Mon', '6/28', '9:30 am', '', '0-3']
    output = 'Home Team - Away Team - Day - Date - Time - Result'
    searchTerm = 'Straw'
    prepList = []
    max = {
        'home': 0,
        'away': 0,
        'day': 0,
        'date': 0,
        'time': 0,
        # 'commentators': 0,
        'result': 0
        }
    for match in matches['us']:
        if searchTerm.lower() in match['home'].lower() or searchTerm.lower() in match['away'].lower():
            for m in max:
                if max[m] < len(match[m]):
                    max[m] = len(match[m])
            prepList.append(match)
    for match in prepList:
        output = output + "\n"
        temp = []
        for key in max:
            temp.append(match[key] + ' '*(max[key]-len(match[key])))
        output = output + ' - '.join(temp)
    print(output)
