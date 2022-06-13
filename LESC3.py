#############################
##   Formating LESC 3 DB   ##
#############################


def formatRosters(db):
    # print(db)
    # print(db['1'][0].get('values',[]))
    # d1 = db['1'][0].get('values',[])
    # d2 = db['2'][0].get('values',[])
    # d3 = db['3'][0].get('values',[])
    # d4 = db['4'][0].get('values',[])
    # rosters = [d1,d2,d3,d4]
    rosters=[]
    for i in db:
        if i == '5' or i == 5:
            pass
        else:
            rosters.append(db[i][0].get('values',[]))
    # print(d1)
    # header = d1[0]
    header = ['team','captain','teammate']
    # print(header)
    roster=[]
    for index in range(0,len(rosters)):
        divN = index+1
        for row in range(1,len(rosters[index])):
            # entry = {'division':'US'}
            entry = {'division':divN}
            # print(rosters[index][row])
            for col in range(len(rosters[index][row])):
                entry[header[col].lower()]=rosters[index][row][col].strip()

            if len(rosters[index][row]) == 3 and rosters[index][row][0] != 'Team Name':
                roster.append(entry)
    # print(roster)
    return roster

def formatStandings(db):
    if '1' in db:
        d1 = db['1'][1].get('values',[])
        d2 = db['2'][1].get('values',[])
        d3 = db['3'][1].get('values',[])
        d4 = db['4'][1].get('values',[])
    else:
        d1 = db[1][1].get('values',[])
        d2 = db[2][1].get('values',[])
        d3 = db[3][1].get('values',[])
        d4 = db[4][1].get('values',[])

    standings = {}
    standings[1]=d1
    standings[2]=d2
    standings[3]=d3
    standings[4]=d4
    # insert rank column
    for division in standings.keys():
        standings[division][0].insert(0,'Rank')
        for row in range(len(standings[division])):
            if row>0:
                standings[division][row].insert(0,str(row))
        # print(standings[division])

    return standings

def getMatches(db):
    print('getMatches')
    # print(ranges)
    matches = {1:[], 2:[], 3:[], 4:[]}
    tz = {1: 'ET', 2: 'ET', 3: 'CET', 4: 'CET'}
    if '1' in db:
        d1 = db['1'][2].get('values',[])
        d2 = db['2'][2].get('values',[])
        d3 = db['3'][2].get('values',[])
        d4 = db['4'][2].get('values',[])
    else:
        d1 = db[1][2].get('values',[])
        d2 = db[2][2].get('values',[])
        d3 = db[3][2].get('values',[])
        d4 = db[4][2].get('values',[])
    matchRaw = {
        1: d1,
        2: d2,
        3: d3,
        4: d4
    }
    # print('===========\nweek')
    # print('upper')
    for div in matchRaw:
        for i in range(len(matchRaw[div])):
            # print(i,' - ', len(values[i]), ' - ', values[i])
            if len(matchRaw[div][i]) >=6 and not ('Home' in matchRaw[div][i][0]):
                home, vs, away, *others = matchRaw[div][i]
                day, date, time, commentators, result = 'TBD','TBD','TBD','','-'
                # day, date, time = 'TBD','TBD','TBD'
                if len(others) == 1:
                    day = others
                elif len(others) == 2:
                    day, date = others
                elif len(others) == 3:
                    day, date, time = others
                elif len(others) == 4:
                    day, date, time, commentators = others
                elif len(others) == 5:
                    day, date, time, commentators, result = others

                tempM = {}
                # print(range(len(values[i])))

                matches[div].append({
                    'home': home,
                    'away': away,
                    'day': day,
                    'date': date,
                    'time': time + ' ' + tz[div],
                    'commentators': commentators,
                    'result': result
                    })

    return matches

def teamsInPlayoffs(db):
    na = db['5'][0].get('values',[])
    eu = db['5'][1].get('values',[])
    playoffs = [na,eu]
    inPlayoffs = False
    list = []
    # print(playoffs)
    # print(len(playoffs))
    rows = [0,6,7,12,13,18]
    # print(rows)
        # print(rows)
    # print(rows - 6)
    # print('here')
    for div in playoffs:
        # print(div)
        for col in [0,-1]:
            for row in rows:
                # print(div[row])
                # print(div[row][col])
                team = div[row][col]
                index = team.find('(')
                if index > 0:
                    team = team[:index].strip()
                team = team.lower()
                # print(team)
                list.append(team)
    # print(list)
    return list

def getAwards(db):
    awardList = []
    awardTable = db['5'][2].get('values',[])
    rosters = formatRosters(db)
    print(awardTable)
    print(rosters)
    for row in awardTable:
        print(row)
        for div in rosters:
            if(len(row))>3:
                if div['team'] == row[3]:
                    awardList.append([row[0],div['captain'],div['teammate']])
                    break

    return awardList
