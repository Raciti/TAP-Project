from flask import Flask, json
from datetime import date, datetime
# cd Desktop/Università/III°\ Anno/II°\ Semestre/TAP/Progetto/
tapserver = Flask(__name__)

f = open('DataframeAll.json')
data = json.load(f)
f.close()

TagPlayer = []
BattleTime = []
Crown = []
KingTower = []
LeftPrincess = []
RigthPrincess = []
CrownOpponent = []
KingTowerOpponent = []
LeftPrincessOpponent = []
RigthPrincessOpponent = []
dim = len(data["TagPlayer"])
for i in range(dim):
    
    TagPlayer.append(data["TagPlayer"][str(i)])
    BattleTime.append(data["BattleTime"][str(i)])
    Crown.append(data["Crown"][str(i)])
    KingTower.append(data["KingTower"][str(i)])
    LeftPrincess.append(data["LeftPrincess"][str(i)])
    RigthPrincess.append(data["RigthPrincess"][str(i)])
    CrownOpponent.append(data["CrownOpponent"][str(i)])
    KingTowerOpponent.append(data["KingTowerOpponent"][str(i)])
    LeftPrincessOpponent.append(data["LeftPrincessOpponent"][str(i)])
    RigthPrincessOpponent.append(data["RigthPrincessOpponent"][str(i)])
@tapserver.route("/return-log")

def return_log():    
    send = { 'timestamp' : datetime.now().isoformat(),
            'Crown' : Crown.pop(),
            'KingTower' : KingTower.pop(),
            'LeftPrincess': LeftPrincess.pop(),
            'RigthPrincess' : RigthPrincess.pop(),
            'CrownOpponent' : CrownOpponent.pop(),
            'KingTowerOpponent' : KingTowerOpponent.pop(),
            'LeftPrincessOpponent' : LeftPrincessOpponent.pop(),
            'RigthPrincessOpponent' : RigthPrincessOpponent.pop()}
    
    
    send_json = json.dumps(send)

    return send_json


if __name__ == "__main__":
    tapserver.run(debug=True,
            host='0.0.0.0',
            port=8000)


# http://localhost:8000/return-log