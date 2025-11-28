import fltk
import shapefile

sf = shapefile.Reader("departement_50m/departements-20140306-50m",  encoding="latin1")

dico_info_departement = {}


for i in range(101):

    dico_info_departement[sf.record(i)[1]] = [sf.shape(i).bbox, sf.shape(i).points] 

    #bbox renvoie une liste de la longitude minimale, latitude minimale, longitude maximale et latitude maximale exprimées en degré dans le système
    #points renvoie les couples de coordonnées (longitude, latitude) des départements également exprimées en degré.

print(dico_info_departement["Mayotte"][1])


fltk.cree_fenetre(1000, 1000)

for k in dico_info_departement.keys() :

    for i in dico_info_departement[k][1]:

        fltk.polygone(i)

fltk.attend_ev()
fltk.ferme_fenetre()