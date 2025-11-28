import fltk
import shapefile
import math

sf = shapefile.Reader("departement_50m/departements-20140306-50m",  encoding="latin1")

dico_info_departement = {}


for i in range(101):

    dico_info_departement[sf.record(i)[1]] = [sf.shape(i).bbox, sf.shape(i).points] 

    #bbox renvoie une liste de la longitude minimale, latitude minimale, longitude maximale et latitude maximale exprimées en degré dans le système
    #points renvoie les couples de coordonnées (longitude, latitude) des départements également exprimées en degré.

print(dico_info_departement["Mayotte"][1])


def deg_to_mercator(dico_coord):

    dico_coord_mercator = {}
    
    liste_coord_mercator = []

    for k in dico_coord.keys():

        for coord in dico_info_departement[k][1]:

            liste_coord_mercator.append((coord[0], math.log(math.tan((math.pi / 4) + (math.radians(coord[1]) / 2)))))

        dico_coord_mercator[k] = liste_coord_mercator

    return dico_coord_mercator


dico_coord_mercator = deg_to_mercator(dico_info_departement)


fltk.cree_fenetre(1000, 1000)

for k,v in dico_coord_mercator.items() :

        fltk.polygone(v)

fltk.attend_ev()
fltk.ferme_fenetre()