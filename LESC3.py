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
    # print(matches)
    # for week in [5,7,9,11]:
    #     values = ranges[week].get('values',[])
    #     for i in range(len(values)):
    #         # print(i,' - ', len(values[i]), ' - ', values[i])
    #         if len(values[i]) >= 6 and not ('Home' in values[i][0]):
    #             # homeTeam, vs, awayTeam, day, date, time, commentating, result = values[i]
    #             # print(values[i])
    #             home, vs, away, *others = values[i]
    #             day, date, time, commentators, result = 'TBD','TBD','TBD','-','-'
    #             if len(others) == 1:
    #                 day = others
    #             elif len(others) == 2:
    #                 day, date = others
    #             elif len(others) == 3:
    #                 day, date, time = others
    #             elif len(others) == 4:
    #                 day, date, time, commentators = others
    #             elif len(others) == 5:
    #                 day, date, time, commentators, result = others
    #
    #             # matches['eu'].append({
    #             matches[2].append({
    #                 'home': home,
    #                 'away': away,
    #                 'day': day,
    #                 'date': date,
    #                 'time': time,
    #                 'commentators': commentators,
    #                 'result': result
    #                 })
    # print(matches)
    return matches
