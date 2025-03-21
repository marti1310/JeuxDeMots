import requests
from math import *
import statistics
import json
import os 

#TODO: 
#    -gérer les relations négatives (réponses négative ou juste supprimer les relations négatives?)
#     -comprendre annotations 
#     - est-ce qu'on doit afficher tous les types de relations (directes, inductives,...) ou demander à l'utilisateur comme fait actuellement?
#    - trier les résultats de relation 1 par ordre décroissant des poids puis vérifier un par un si r2 ou pas 

#raffsem  id=1
#raffmorpho id=2

with open("relations.json", "r") as f:
    data = json.load(f)


url = "https://jdm-api.demo.lirmm.fr/v0/"

def relationDepuisUnNoeud(node,relationid):
    directory = "requetes/relations"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = os.path.join(directory, f"{node}_{nomRelationParId(relationid)}.json")
    if os.path.exists(filename):
        with(open(filename,"r")) as f:
            return json.load(f)
    else: 
        req = f"{url}relations/from/{node}?types_ids={relationid}"
        r = requests.get(req)

        if r.status_code == 200:
            data = r.json()
            data_sorted = sorted(data["relations"], key=lambda x: x["w"], reverse=True) 
            data = {**data, "relations": data_sorted} #On trie les relations par poids decroissant

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data
        
        else:
            print(f"Erreur {r.status_code} lors de la requête : {req}")
            return None
        


#https://jdm-api.demo.lirmm.fr/v0/relations/to/{node2_name}
def relationVersUnNoeud(node,relationid):
    directory = "requetes/relations"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, f"{nomRelationParId(relationid)}_{node}.json")
    if os.path.exists(filename):
        with(open(filename,"r")) as f:
            return json.load(f)
    else: 
        req = f"{url}relations/to/{node}?types_ids={relationid}"
        r = requests.get(req)
        

        if r.status_code == 200:
            data = r.json()
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return data
        else:
            print(f"Erreur {r.status_code} lors de la requête : {req}")
            return None
    
#https://jdm-api.demo.lirmm.fr/v0/node_by_id/{node_id}
#Fct qui prend en paramètre un id de noeud et qui retourne les informations du noeud
def noeudParId(nodeid):
    req = url+"node_by_id/"+str(nodeid)
    return requests.get(req).json()



#Fct qui prend en paramètre deux listes de relations et qui retourne une liste de tuples (noeud_commun, poids)
def intersection(rel_depuis,rel_vers):
    res = []
    for r in rel_depuis["relations"][:10]:
        for s in rel_vers["relations"]:
            if r["node2"] == s["node1"] and r["w"]>0 and s['w']>0: #Pour l'instant on supprimes les relations avec des poids négatifs
                w = statistics.geometric_mean([r["w"],s["w"]])
                res.append((r["node2"],round(w,1)))
    res = sorted(res,key=lambda x: x[1],reverse=True)
    return res


#Fct qui prend en paramètre un id de noeud et qui retourne son nom
def nomNoeudParId(nodeid):
    #print(noeudParId(nodeid))
    return noeudParId(nodeid)["name"]


#Fct qui prend en paramètre un id de relation et qui retourne son nom
def nomRelationParId(relid):
    if relid<2002:
        return data[relid]["nom"]
    else: return relid

#Fct qui prend en paramètre un nom de relation et qui retourne son id
def idRelationParNom(nom):
    for i in range(len(data)):
        if data[i]["nom"] == nom:
            return i
    return -1

def __main__():
    print("Bienvenue dans le projet de recherche de relations entre les mots")

    print("Veuillez entrer le mot source")
    mot_source = input()

    print("Veuillez entrer le mot cible")
    mot_cible = input()

    print("Veuillez entrer le nom de la relation")
    nom_relation = input()
    id_relation_2 = idRelationParNom(nom_relation)
    while id_relation_2 == -1:
        print("La relation n'existe pas")
        print("Veuillez entrer le nom de la relation")
        nom_relation = input()
        id_relation_2 = idRelationParNom(nom_relation)
    
    print("Quel type d'inférence voulez-vous faire ? (déductive (d) ,inductive (i) ,transitive (t), synonyme (s))")
    type_inference = input()
    while type_inference not in ["d","i","t","s"]:
        print("Type d'inférence non reconnu")
        print("Quel type d'inférence voulez-vous faire ? (déductive (d) ,inductive (i) ,transitive (t), synonyme (s))")
        type_inference = input()
    if type_inference == "d":
        id_relation_1 = 6
    elif type_inference == "i":
        id_relation_1 = 8
    elif type_inference == "t": 
        id_relation_1 = id_relation_2
    elif type_inference == "s":
        id_relation_1 = 5
    
    print("Chargement des résultats...")
    rel_depuis = relationDepuisUnNoeud(mot_source,id_relation_1)
    rel_vers = relationVersUnNoeud(mot_cible,id_relation_2)
    res = intersection(rel_depuis,rel_vers)
    if len(res) == 0:
        print("Il n'y a pas de relation entre les deux mots")

    else:
        print("Résultats: (max 10)")              
        for i in range (len(res)):
            print(i+1,"| oui |",mot_source,nomRelationParId(id_relation_1),nomNoeudParId(res[i][0]),"&",nomNoeudParId(res[i][0]),nomRelationParId(id_relation_2),mot_cible,"| ",res[i][1])



if __name__ == "__main__":
   __main__()

