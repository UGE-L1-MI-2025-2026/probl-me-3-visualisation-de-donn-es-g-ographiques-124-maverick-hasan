import fltk
import shapefile
import math
import random
import sys
DEPARTEMENTS_A_EXCLURE = ["Guyane", "Martinique", "Guadeloupe", "La Réunion", "Mayotte"]
FENETRE_TAILLE = 500
MARGE = 0.9
def etape1_chargement_et_filtrage():
    try :
        sf = shapefile.Reader("departement_50m/departements-20140306-50m", encoding="latin1")
    except :
        print("Erreur: Fichier 'departement_50m/departements-20140306-50m' non trouvé.")
        sys.exit(1)
    dico_info_departement_filtre = {}
    for shape_record in sf.iterShapeRecords():
        nom_departement = shape_record.record[1]
        if nom_departement not in DEPARTEMENTS_A_EXCLURE:
            dico_info_departement_filtre[nom_departement] = shape_record.shape.points 
    print(dico_info_departement_filtre.keys())
    return dico_info_departement_filtre
def etape2_projection_mercator(dico_coord):
    dico_coord_mercator = {}
    x_min_all, x_max_all = float('inf'), float('-inf')
    y_min_all, y_max_all = float('inf'), float('-inf')
    for k, liste_points_deg in dico_coord.items(): 
        liste_coord_mercator = []
        for lon, lat in liste_points_deg:
            x_mercator = math.radians(lon)
            y_rad = math.radians(lat)
            y_mercator =math.log(math.tan((math.pi / 4) + (y_rad / 2))) 
            liste_coord_mercator.append((x_mercator, y_mercator))
            x_min_all = min(x_min_all, x_mercator)
            x_max_all = max(x_max_all, x_mercator)
            y_min_all = min(y_min_all, y_mercator)
            y_max_all = max(y_max_all, y_mercator)
        dico_coord_mercator[k] = liste_coord_mercator
    return dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all
def etape3_transformation_en_ecran(dico_coord_mercator, x_min, x_max, y_min, y_max):
    centre_fenetre_en_pixel = FENETRE_TAILLE / 2
    amplitude_x = x_max - x_min
    amplitude_y = y_max - y_min
    max_amplitude = max(amplitude_x, amplitude_y) 
    if max_amplitude == 0:
        coefficient_ajustement = 1 
    else:
        coefficient_ajustement = (FENETRE_TAILLE * MARGE) / max_amplitude
    centre_x_mercator = x_min + amplitude_x / 2
    centre_y_mercator = y_min + amplitude_y / 2
    dico_coord_screen = {}
    for k, liste_mercator in dico_coord_mercator.items():
        liste_coord_screen = []
        for lon_mercator, y_mercator in liste_mercator:
            vecteur_x_en_pixel = (lon_mercator - centre_x_mercator) * coefficient_ajustement
            vecteur_y_en_pixel = (y_mercator - centre_y_mercator) * coefficient_ajustement
            coordonnée_x_pixel = int(centre_fenetre_en_pixel + vecteur_x_en_pixel)
            coordonée_y_pixel = int(centre_fenetre_en_pixel - vecteur_y_en_pixel) 
            liste_coord_screen.append((coordonnée_x_pixel, coordonée_y_pixel))
        dico_coord_screen[k] = liste_coord_screen
    return dico_coord_screen
def etape4_dessiner_carte(dico_coord_screen):
    fltk.cree_fenetre(FENETRE_TAILLE, FENETRE_TAILLE)
    for v in dico_coord_screen.values() :
        fltk.polygone(
            v, 
            couleur='black', 
            remplissage=random.choice([
    "#440154", "#45095E", "#461167", "#471971", 
    "#47227A", "#452C83", "#43358B", "#413E91", 
    "#3F4797", "#3D509D", "#3C588C", "#375F94", 
    "#31669C", "#2C6EA2", "#2875A8", "#257DAE", 
    "#2385B4", "#228CBD", "#2494C6", "#259CCA", 
    "#26A084", "#28A684", "#2BAE84", "#30B583", 
    "#37BC80", "#41C37B", "#4CCD76", "#59D270", 
    "#67D66A", "#75D95C", "#84D44B", "#93D638", 
    "#A3D823", "#B3DA11", "#C3DC04", "#D3DE00", 
    "#E2DF04", "#F1E018", "#FEE033", "#FDE725"
    ]), 
            epaisseur=1
        )
def dessiner_pays() :
    dico_info_departement = etape1_chargement_et_filtrage()
    dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all = etape2_projection_mercator(dico_info_departement)
    dico_coord_screen = etape3_transformation_en_ecran(dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all)
    etape4_dessiner_carte(dico_coord_screen)
def dessiner_indicateur() :
    nombre = 0
    degrade_couleur = [
    "#440154", "#45095E", "#461167", "#471971", 
    "#47227A", "#452C83", "#43358B", "#413E91", 
    "#3F4797", "#3D509D", "#3C588C", "#375F94", 
    "#31669C", "#2C6EA2", "#2875A8", "#257DAE", 
    "#2385B4", "#228CBD", "#2494C6", "#259CCA", 
    "#26A084", "#28A684", "#2BAE84", "#30B583", 
    "#37BC80", "#41C37B", "#4CCD76", "#59D270", 
    "#67D66A", "#75D95C", "#84D44B", "#93D638", 
    "#A3D823", "#B3DA11", "#C3DC04", "#D3DE00", 
    "#E2DF04", "#F1E018", "#FEE033", "#FDE725"
    ]
    i = 0
    n = FENETRE_TAILLE // len(degrade_couleur)
    bord_1_x = FENETRE_TAILLE * 0.98
    bord_1_y = 0
    bord_2_x = FENETRE_TAILLE
    bord_2_y = FENETRE_TAILLE
    for rectangle in range(0,len(degrade_couleur)) :
        fltk.rectangle(bord_1_x, bord_1_y , bord_2_x , bord_2_y , remplissage = degrade_couleur[i])
        if i % 5 == 0 :
            fltk.texte(bord_1_x - round(FENETRE_TAILLE * 0.045) , bord_1_y, str(nombre), couleur="black", taille=round(FENETRE_TAILLE * 0.015))
        bord_1_y += n
        bord_2_y += n
        i += 1
        nombre += 50
def main():
    dessiner_pays()
    dessiner_indicateur()
    fltk.attend_ev()
main()