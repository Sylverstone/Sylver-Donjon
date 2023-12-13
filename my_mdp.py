import json
from cryptography.fernet import Fernet
import os
os.chdir("Source")
with open('SET/cle.key', 'rb') as fichier_cle:
    cle = fichier_cle.read()

fernet = Fernet(cle)
with open('SET/mot_de_passe.json', 'r') as fichier_json:
    data = json.load(fichier_json)
    mot_de_passe_chiffre = data['mot_de_passe'].encode('utf-8')
    mot_de_passe_dechiffre = fernet.decrypt(mot_de_passe_chiffre)

def mdp():
    return mot_de_passe_dechiffre.decode('utf-8')

if __name__ == "__main__":
    print(mdp())

