#############################
##   Formating LESC 3 DB   ##
#############################


def formatRosters(db):
    # print(db)
    # print(db['1'][0].get('values',[]))
    d1 = db['1'][0].get('values',[])
    d2 = db['2'][0].get('values',[])
    d3 = db['3'][0].get('values',[])
    d4 = db['4'][0].get('values',[])
    rosters = [d1,d2,d3,d4]
    # print(d1)
    header = d1[0]
    header = ['team','captain','teammate']
    print(header)
    roster=[]
    for index in range(0,len(rosters)):
        divN = index+1
        for row in range(2,len(rosters[index])):
            # entry = {'division':'US'}
            entry = {'division':divN}
            # print(rosters[index][row])
            for col in range(len(rosters[index][row])):
                entry[header[col].lower()]=rosters[index][row][col].strip()

            if len(rosters[index][row]) == 3 and rosters[index][row][0] != 'Team Name':
                roster.append(entry)
    # print(roster)
    return roster
