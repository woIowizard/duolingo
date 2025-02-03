cookie = ''

import requests,json,time,argparse,base64,random,datetime
p=argparse.ArgumentParser()
p.add_argument('-c',help='cookie')
p.add_argument('-d',action='store_true',help='2x xp boost')
p.add_argument('-e',action='store_true',help='health refill')
p.add_argument('-n',help='number of repetitions. default 1, 0 for inf')
p.add_argument('-p',action='store_true',help='progress lessons')
p.add_argument('-l',action='store_true',help='legendary lessons')
p.add_argument('-P',action='store_true',help='patient mode')
p.add_argument('-g',help='claim rewards chest. \'list\' to see options')
p.add_argument('-k',help='update stats key. \'list\' to see options')
p.add_argument('-v',help='increase stat value')
args = p.parse_args()

if args.c: cookie=args.c
elif not cookie: print('[-] missing session cookie');quit()
try: m = cookie.split('.')[1];uid = json.loads(base64.b64decode((m+'='*(-len(m)%3))).decode())['sub']
except: print('[-] invalid session cookie');quit()
try: n = int(args.n) if args.n else 1
except: print('[-] number of reps must be a non-negative integer');quit()
    
h={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0", "Accept": "application/json; charset=UTF-8", "Accept-Language": "en-US,en;q=0.5", "Content-Type": "application/json; charset=UTF-8", "Referer": "https://www.duolingo.com/", "X-Amzn-Trace-Id": "User=%s"%uid, "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.duolingo.com", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site", "Priority": "u=4", "Te": "trailers"}

j = json.loads(requests.get('https://www.duolingo.com/2017-06-30/users/%s?fields=rewardBundles,trackingProperties,currentCourse'%uid,cookies={'jwt_token':cookie},headers=h).text)
L = j['trackingProperties']['learning_language']

if args.k:
    m = ['QUESTS','LESSONS', 'FIVE_CORRECT_IN_A_ROW', 'TEN_CORRECT_IN_A_ROW', 'EIGHTY_ACCURACY_LESSONS', 'NINETY_ACCURACY_LESSONS', 'PERFECT_LESSONS', 'XP', 'COMBO_XP', 'SPEAK_CHALLENGES', 'LISTEN_CHALLENGES', 'SECONDS_SPENT_LEARNING','EXTEND_STREAK','DEEPEST_PATH_NODE_SESSIONS','MATH_SESSIONS','MUSIC_SESSIONS','STORIES']
    try: k = m[int(args.k)]
    except: print('========== STAT OPTIONS ==========\n'+'\n'.join('%s\t%s'%(i,l) for i,l in enumerate(m))+'\n');quit()
    try: v = int(args.v);assert v>0
    except: print('[-] value must be positive integer');quit()
    print('[=] increasing stat %s by %s'%(k,args.v))
    t = datetime.datetime.now(datetime.UTC)
    r = requests.post('https://goals-api.duolingo.com/users/%s/progress/batch'%uid,cookies={'jwt_token':cookie},headers=h,json={"metric_updates": [{"metric":k, "quantity":v}], "timestamp":t.strftime("%Y-%m-%dT%H:%M:%S.")+str(t.microsecond)[:3]+"Z", "timezone": "Asia/Srednekolymsk"})
    try: assert json.loads(r.text)['message']=='SUCCESS'; print('[+] update success')
    except: print('[-] update failed with status code %s'%(r.status_code));print('[DEBUG] %s'%r.text)
elif args.d or args.e:
    print('[=] attempting to get %s'%('health refill' if args.e else 'xp boost'))
    r = requests.post('https://www.duolingo.com/2017-06-30/users/%s/shop-items'%uid,cookies={'jwt_token':cookie},headers=h,json={"isFree": True, "itemName": "health_refill" if args.e else 'xp_boost_15', "learningLanguage":L})
    try: 
        if args.e: assert json.loads(r.text)['itemName']=='health_refill';print('[+] health refilled')
        else: print('[+] success. xp boost until %s'%datetime.datetime.fromtimestamp(json.loads(r.text)['expectedExpirationDate']).strftime('%Y-%m-%d %H:%M:%S'))
    except: print('[-] update failed with status code %s'%(r.status_code));print('[DEBUG] %s'%r.text)
elif args.g:
    tt=ta=i=0
    if args.g == 'skill': tt,ta='SKILL_COMPLETION_BALANCED',30
    while not n or i<n:
        if i: j = json.loads(requests.get('https://www.duolingo.com/2017-06-30/users/%s?fields=rewardBundles,trackingProperties'%uid,cookies={'jwt_token':cookie},headers=h).text)
        r = sorted([c for l in j['rewardBundles'] for c in l['rewards'] if not c['consumed'] and 'currency' in c and c['currency']=='GEMS'],key=lambda x:(x['amount'],x['id']))
        try: k = [c for c in r if c['amount']==ta and c['id'].split('-')[0]==tt][0] if tt else r[int(args.g)]
        except: print('%s========== AVAILABLE CHESTS ==========\n'%('[-] [CHEST %s%s] chest not found\n\n'%(i+1,'/%s'%n if n else '') if tt else '')+'\n'.join('{0}\t{1:3} gems\t{2}'.format(i,l['amount'],l['id'].split('-')[0]) for i,l in enumerate(r))+'\n');quit()
        ta,tt = k['amount'],k['id'].split('-')[0]
        print('[=] [CHEST %s%s] claiming chest %s-%s********'%(i+1,'/%s'%n if n else '',k['id'].split('-')[0],k['id'].split('-')[1][:5]))
        r = requests.patch('https://www.duolingo.com/2017-06-30/users/%s/rewards/%s'%(uid,k['id']),cookies={'jwt_token':cookie},headers=h,json={"consumed":True,"fromLanguage":"en","learningLanguage":L})
        try: assert r.status_code==200; print('[+] [CHEST %s%s] claimed %s gems'%(i+1,'/%s'%n if n else '',k['amount']));i+=1
        except: print('[-] [CHEST %s%s] failed with status code %s'%(i+1,'/%s'%n if n else '',r.status_code));print('[DEBUG] %s'%r.text);quit()
else:
    print('[=] running %s %s lessons%s'%(n if n else 'endless','legendary' if args.l else 'progress' if args.p else 'practice',', patient mode' if args.P else ''))
    i=0
    while not n or i<n:
        if i: j = json.loads(requests.get('https://www.duolingo.com/2017-06-30/users/%s?fields=rewardBundles,trackingProperties,currentCourse'%uid,cookies={'jwt_token':cookie},headers=h).text)
        ui,li,si,ki,md,type = [(u['unitIndex'],i,l['finishedSessions'],(None if l['type']=='story' else l['pathLevelMetadata']['skillId'] if 'skillId' in l['pathLevelMetadata'] else l['pathLevelMetadata']['anchorSkillId']),l['pathLevelMetadata'],l['type']) for s in j['currentCourse']['pathSectioned'] for u in s['units'] for i,l in enumerate(u['levels']) if l['state']=='active'][0]
        if args.p and type=='chest': 
            r = max([c for l in j['rewardBundles'] for c in l['rewards'] if not c['consumed'] and 'currency' in c and c['currency']=='GEMS' and c['id'].split('-')[0]=='PATH_CHEST'],key=lambda x:x['amount'])['id']
            print('[=] claiming path chest %s'%(r))
            r = requests.patch('https://www.duolingo.com/2017-06-30/users/%s/rewards/%s'%(uid,r),cookies={'jwt_token':cookie},headers=h,json={"consumed":True,"fromLanguage":"en","learningLanguage":L,'pathLevelSpecifics':md})
            try: assert r.status_code==200; print('[+] [CHEST] claim success');continue
            except: print('[-] [CHEST] failed with status code %s'%(i+1,'/%s'%n if n else '',r.status_code));print('[DEBUG] %s'%r.text);quit()
        print('[=] [LESSON %s%s] initialising %s lesson%s'%(i+1,'/%s'%n if n else '','legendary' if args.l else type if args.p else 'practice',': unit %s section %s lesson %s'%(ui+1,li+1,si+1) if args.p else ''))
        if args.p and type=='story': 
            r = requests.post('https://stories.duolingo.com/api2/stories/%s/complete'%md['storyId'],headers=h,cookies={'jwt_token':cookie},json={"awardXp":True,"completedBonusChallenge":False,"dailyRefreshInfo":None,"fromLanguage":"en","hasXpBoost":True,"illustrationFormat":"svg","isFeaturedStoryInPracticeHub":False,"isLegendaryMode":False,"isListenModeReadOption":False,"isV2Redo":False,"isV2Story":True,"learningLanguage":L,"masterVersion":False,"maxScore":6,"mode":"READ","numHintsUsed":0,"pathLevelSpecifics":md,"score":5,"startTime":round(time.time())})
            try: assert r.status_code==200; print('[+] [STORY] completion success');continue
            except: print('[-] [STORY] failed with status code %s'%(i+1,'/%s'%n if n else '',r.status_code));print('[DEBUG] %s'%r.text);quit()
        d1={"challengeTypes": ["assist", "characterIntro", "characterMatch", "characterPuzzle", "characterSelect", "characterTrace", "characterWrite", "completeReverseTranslation", "definition", "dialogue", "extendedMatch", "extendedListenMatch", "form", "freeResponse", "gapFill", "judge", "listen", "listenComplete", "listenMatch", "match", "name", "listenComprehension", "listenIsolation", "listenSpeak", "listenTap", "orderTapComplete", "partialListen", "partialReverseTranslate", "patternTapComplete", "radioBinary", "radioImageSelect", "radioListenMatch", "radioListenRecognize", "radioSelect", "readComprehension", "reverseAssist", "sameDifferent", "select", "selectPronunciation", "selectTranscription", "svgPuzzle", "syllableTap", "syllableListenTap", "speak", "tapCloze", "tapClozeTable", "tapComplete", "tapCompleteTable", "tapDescribe", "translate", "transliterate", "transliterationAssist", "typeCloze", "typeClozeTable", "typeComplete", "typeCompleteTable", "writeComprehension"], "fromLanguage": "en", "isFinalLevel": bool(args.l), "isV2": True, "juicy": True, "learningLanguage": L, "shakeToReportEnabled": True, "smartTipsVersion": 2} 
        if args.l: d1['levelIndex']=0;d1['skillId']=ki;d1['type']='LEGENDARY_LEVEL'
        elif args.p:
            if type=='skill': d1['isCustomIntroSkill']=False;d1["levelIndex"]=li;d1["levelSessionIndex"]=si;d1['pathExperiments']=[];d1['showGrammarSkillSplash']=False;d1["skillId"]=ki;d1['type']='LESSON'
            elif type=='unit_review': d1["levelSessionIndex"]=si;d1["skillIds"]=[ki];d1['type']='UNIT_REVIEW'
            else: d1["levelSessionIndex"]=si;d1["skillIds"]=[ki];d1['type']='UNIT_PRACTICE';d1['pathExperiments']=[]
        else: d1['type']='GLOBAL_PRACTICE'
        
        r = requests.post('https://www.duolingo.com/2017-06-30/sessions',cookies={'jwt_token':cookie},headers=h,json=d1)
        try: 
            qns=json.loads(r.text)
            starttime,cid = qns['challenges'][0]['challengeResponseTrackingProperties']['generation_timestamp']//1000,qns['id']
        except: print('[-] [LESSON %s%s] lesson initialisation failed with status code %s'%(i+1,'/%s'%n if n else '',r.status_code));print('[DEBUG] %s'%r.text);quit()
        
        print('[+] [LESSON %s%s] initialisation successful. id: %s'%(i+1,'/%s'%n if n else '',cid))
        h2 = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0", "Accept": "application/json; charset=UTF-8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Content-Type": "application/json; charset=UTF-8", "X-Amzn-Trace-Id": "User=%s"%uid, "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.duolingo.com", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin", "Priority": "u=0", "Te": "trailers", "Idempotency-Key":cid}
        qns['heartsLeft']=0; qns['startTime']=starttime; qns['enableBonusPoints']=True; qns['failed']=False; qns['maxInLessonStreak']=len(qns['challenges'])
        if args.l: qns['xpPromised']=200;qns['dailyRefreshInfo']=None;qns['pathLevelSpecifics']={"skillId":si,"crownLevelIndex":0};qns['shouldLearnThings']=True
        elif args.p: 
            qns['dailyRefreshInfo']=None;qns['pathLevelSpecifics']=md
            if type=='skill': qns['shouldLearnThings']=True
        else: qns['shouldAward5XpFromGlobalPractice']=True;qns['shouldLearnThings']=True
        
        if args.P:
            r = round(random.random()*120+45)
            print('[=] [LESSON %s%s] sleeping %s secs'%(i+1,'/%s'%n if n else '',r))
            time.sleep(r)
            qns['endTime']=round(time.time())
        else: qns['endTime']=round(time.time()+random.random()*120+45)
        
        r = requests.put('https://www.duolingo.com/2017-06-30/sessions/'+cid,cookies={'jwt_token':cookie},headers=h2,json=qns)
        try: print('[+] [LESSON %s%s] completed. gained %s xp'%(i+1,'/%s'%n if n else '',json.loads(r.text)['xpGain']))
        except: print('[-] [LESSON %s%s] lesson completion failed with status code %s'%(i+1,'/%s'%n if n else '',r.status_code));print('[DEBUG] %s'%r.text);quit()
        i+=1
print('')
