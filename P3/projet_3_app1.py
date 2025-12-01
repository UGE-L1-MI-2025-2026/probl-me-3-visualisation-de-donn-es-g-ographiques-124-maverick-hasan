import fltk
import shapefile
import math

sf = shapefile.Reader("departement_50m/departements-20140306-50m",  encoding="latin1")

dico_info_departement = {}


for i in range(101):

    dico_info_departement[sf.record(i)[1]] = [sf.shape(i).bbox, sf.shape(i).points] 

    #bbox renvoie une liste de la longitude minimale, latitude minimale, longitude maximale et latitude maximale exprimées en degré dans le système
    #points renvoie les couples de coordonnées (longitude, latitude) des départements également exprimées en degré.


DEPARTEMENTS_A_EXCLURE = ["Guyane", "Martinique", "Guadeloupe", "La Réunion", "Mayotte"]


dico_info_departement_filtre = {
    k: v for k, v in dico_info_departement.items() 
    if k not in DEPARTEMENTS_A_EXCLURE
}
dico_info_departement = dico_info_departement_filtre


def deg_to_mercator(dico_coord):

    dico_coord_mercator = {}
    x_min_all, x_max_all = float('inf'), float('-inf')
    y_min_all, y_max_all = float('inf'), float('-inf')
    C_AMPLIFICATION = 60.0

    for k in dico_coord.keys():
        liste_coord_mercator = []
        for lon, lat in dico_coord[k][1]:

            #Projection (X = Longitude)
            lon_mercator = lon
            
            #Projection (Y = Mercator)
            lat_rad = math.radians(lat)
            y_mercator = math.log(math.tan((math.pi / 4) + (lat_rad / 2)))
            
            y_mercator_ajuste = y_mercator * C_AMPLIFICATION 

            # Remplacer la ligne initiale par la nouvelle coordonnée projetée et ajustée
            liste_coord_mercator.append((lon_mercator, y_mercator_ajuste))
            
            #Mise à jour des bornes
            x_min_all = min(x_min_all, lon_mercator)
            x_max_all = max(x_max_all, lon_mercator)
            y_min_all = min(y_min_all, y_mercator_ajuste)
            y_max_all = max(y_max_all, y_mercator_ajuste)


        dico_coord_mercator[k] = liste_coord_mercator
        
    # La fonction retourne le dictionnaire ET les bornes globales
    return dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all

dico_coord_mercator, x_min, x_max, y_min, y_max = deg_to_mercator(dico_info_departement)
FENETRE_TAILLE = 1000
MARGE = 0.9
screen_center = FENETRE_TAILLE / 2

x_range = x_max - x_min
y_range = y_max - y_min
scale_factor = (FENETRE_TAILLE * MARGE) / max(x_range, y_range)

# 3. Calcul du centre des données (point de pivot de la carte)
map_center_x = x_min + x_range / 2
map_center_y = y_min + y_range / 2


dico_coord_screen = {}

for k, liste_mercator in dico_coord_mercator.items():
    liste_coord_screen = []
    for lon_mercator, y_mercator in liste_mercator:
        
        # Centrage des données (Translation à l'origine (0,0))
        centered_x = lon_mercator - map_center_x
        centered_y = y_mercator - map_center_y
        
        # Mise à l'échelle
        scaled_x = centered_x * scale_factor
        scaled_y = centered_y * scale_factor
        
        # Translation vers le centre de l'écran (500, 500) et Inversion de l'axe Y
        x_screen = int(screen_center + scaled_x)
        y_screen = int(screen_center - scaled_y) 

        liste_coord_screen.append((x_screen, y_screen))

    dico_coord_screen[k] = liste_coord_screen

fltk.cree_fenetre(FENETRE_TAILLE, FENETRE_TAILLE)
for k,v in dico_coord_screen.items() :
        fltk.polygone(v, couleur='black', remplissage='lightgreen', epaisseur=1)
fltk.attend_ev()