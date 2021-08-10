team_db = {'LESC1':[
  {'name':'Pineapple On Pizza'	,'captain':'SassyBrenda' 	,'teammate':'KarmaKredits','division': 'US'},
  {'name':'Overconfident'	,'captain':'MrPriority'	,'teammate':'ChillCatDad','division': 'EU'},
  {'name':'The Ginger Brothers'	,'captain':'Noblent'	,'teammate':'ItsJeffTTV'		,'division': 'US'},
  {'name':'Up Your ARSEnal'	,'captain':'harm'	,'teammate':'yolomcshweg','division': 'EU'},
  {'name':'JustZees League' 	,'captain':'Shwa_Zee'	,'teammate':'justin.;p'		,'division': 'US'},
  {'name':'PERKELE'	,'captain':'Sant.'	,'teammate':'Normy','division': 'EU'},
  {'name':'Strawberries > Grapes'	,'captain':'Semper1515'	,'teammate':'SickLarry' 		,'division': 'US'},
  {'name':'LouisJames & His Cousin'	,'captain':'LouisJames'	,'teammate':'BigLez_THE_Bong_Head','division': 'EU'},
  {'name':'5'	,'captain':'Anubis' 	,'teammate':'Laggittarius'		,'division': 'US'},
  {'name':'AlphaKenny1'	,'captain':'DannyofthePaul'	,'teammate':'Azeria','division': 'EU'},
  {'name':'BobbyBuddy'	,'captain':'RuddyBuddy' 	,'teammate':'BobbyNay'		,'division': 'US'},
  {'name':'6'	,'captain':'Jamal751'	,'teammate':'Piers','division': 'EU'},
  {'name':'Big Cox'	,'captain':'Boxidize'	,'teammate':'Vl0xx' 		,'division': 'US'},
  {'name':'Fighting 13th'	,'captain':'Elephantagon' 	,'teammate':'MartPorsche','division': 'EU'},
  {'name':'Flying Avocados'	,'captain':'Avocado'	,'teammate':'FlyZK'		,'division': 'US'},
  {'name':'Gooch Slime'	,'captain':'Eddd_'	,'teammate':'jjjamie__','division': 'EU'},
  {'name':'Tiny Games'	,'captain':'Tiny' 	,'teammate':'CSmith_Games'		,'division': 'US'},
  {'name':'DNRB'	,'captain':'Rorymtb'	,'teammate':'Daughton','division': 'EU'},
  {'name':'Nked Dommer-nuts'	,'captain':'NK_XIV'	,'teammate':'Mdomm'		,'division': 'US'},
  {'name':'Failing 13th'	,'captain':'Benny_07' 	,'teammate':'Thomas','division': 'EU'},
  {'name':'Boost Over Ball'	,'captain':'TheDongerLord'	,'teammate':'VHP' 		,'division': 'US'},
  {'name':'O7'	,'captain':'HighSolution136'	,'teammate':'Ragdoll139','division': 'EU'},
  {'name':'Never Wallalols'	,'captain':'GingerSoccerMom'	,'teammate':'Midori'		,'division': 'US'},
  {'name':'I Need Boost', 'captain':	'flyabl3' 	,'teammate':'holy nuggie','division': 'EU'},
  {'name':'The 2 Meatballs'	,'captain':'0val'	,'teammate':'Elekid123','division': 'EU'}
]}

participant_db = {'commissioners:':[],'players':[],'substitutes':['bagayaro','Bagwer_RL','excel メ','GoodNeighbor','hugo_chakka','IcedColed (Cole)','JJ','r4l','Shvrkii','thebronxbomber','Wildered'],'commentator':[],'viewers':[],'collaborators:':[]}

player_db = [{'player':'VHP','season':['S1 :flag_us: Division'],'awards':[':first_place: S1 US Champion',':sweat: S1 Playoff Contender', ':goal: S1 Team Golden Boot',':angel: S1 Team Guardian Angel',':soccer: S1 OG Participant'],'teams':['Boost Over Ball'],'teammates':['TheDongerLord']},
{'player':'KarmaKredits','season':['S1 US Division'],'awards':['S1 Playoff Contender','S1 OG Participant'],'teams':['Pineapple on Pizza'],'teammates':['Sassy Brenda']},
{'player':'Ragdoll139','season':['S1 EU Division'],'awards':['S1 Playoff Contender','S1 Team Golden Boot','S1 OG Participant'],'teams':['O7'],'teammates':['HighSolution136']},
{'player':'GingerSoccerMom','season':['S1 US Division'],'awards':['S1 Playoff Contender','S1 OG Participant'],'teams':['Never Wallalols'],'teammates':['Midori']}]

match_db = {}

regex = '^(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)$'
standingsUS = """Rank	Team	W	L	SP	SW	GF	GA	GD	PTS
1	Boost Over Ball	24	2	8	8	127	47	80	32
2	BobbyBuddy	20	10	8	6	112	71	41	26
3	Never Wallalols	19	11	8	6	110	81	29	25
4	Anubis & Laggittarius	19	13	8	6	102	83	19	25
5	Pineapple On Pizza	18	14	8	5	96	92	4	23
6	Nked Dommer-nuts	18	17	8	5	97	100	-3	23
7	Big Cox	16	13	8	4	89	66	23	20
8	Avocado & FlyZK	13	17	8	3	78	95	-17	16
9	The Ginger Brothers	14	22	8	2	102	126	-24	16
10	JustZees League	9	18	8	2	65	79	-14	11
11	Strawberries > Grapes	9	21	8	2	66	118	-52	11
12	Tiny Games	3	24	8	0	59	145	-86	3"""