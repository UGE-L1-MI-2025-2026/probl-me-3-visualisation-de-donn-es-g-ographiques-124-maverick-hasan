import fltk
import shapefile
import math
import random
import sys

DEPARTEMENTS_A_EXCLURE = ["Guyane", "Martinique", "Guadeloupe", "La Réunion", "Mayotte"]
FENETRE_TAILLE = 1000
MARGE = 0.9
DEGRADE_COULEUR = [
    "#440154", "#45095E", "#461167", "#471971", 
    "#47227A", "#452C83", "#43358B", "#413E91", 
    "#3F4797", "#3D509D", "#3C588C", "#375F94", 
    "#31669C", "#2C6EA2", "#2875A8", "#257DAE", 
    "#2385B4", "#228CBD", "#2494C6", "#259CCA", 
    "#26A084", "#28A684", "#2BAE84", "#30B583", 
    "#37BC80", "#41C37B", "#4CCD76", "#59D270", 
    "#67D66A", "#75D95C", "#84D44B", "#93D638", 
    "#A3D823", "#B3DA11", "#C3DC04", "#D3DE00", 
    "#E2DF04", "#F1E018", "#FEE033", "#FDE725"]
DICO_SEGMENT = {}
COORDONEE_CENTRE_CERCLES = {}


def normaliser_nom_departement(nom):
    remplacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a',
        'ù': 'u', 'û': 'u',
        'ô': 'o',
        'î': 'i', 'ï': 'i',
        'ç': 'c',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'À': 'A', 'Â': 'A',
        'Ù': 'U', 'Û': 'U',
        'Ô': 'O',
        'Î': 'I', 'Ï': 'I',
        'Ç': 'C'
    }
    nom_propre = nom.strip() 
    liste_caracteres = list(nom_propre)
    for i in range(len(liste_caracteres)):
        caractere = liste_caracteres[i]
        if caractere in remplacements:
            liste_caracteres[i] = remplacements[caractere]   
    nom_final = "".join(liste_caracteres)
    return nom_final.lower()
    

def recuperer_csv(fichier_csv):
    dico_stat = {}
    with open(fichier_csv, mode='r', newline='', encoding='latin-1') as fichier:
        fichier.readline()
        for i in range(0,96) :
            ligne = fichier.readline().strip().split(',')
            nom_normalise = normaliser_nom_departement(ligne[0])
            dico_stat[nom_normalise] = ligne[1:4]
    return dico_stat


def etape1_chargement_et_filtrage(dico_stat):
    try :
        sf = shapefile.Reader("departement_50m/departements-20140306-50m", encoding="latin1")
    except :
        print("Erreur: Fichier 'departement_50m/departements-20140306-50m' non trouvé.")
        sys.exit(1)
    DEPARTEMENTS_A_EXCLURE_NORMALISES = [normaliser_nom_departement(d) for d in DEPARTEMENTS_A_EXCLURE]
    dico_info_departement_filtre = {}
    for shape_record in sf.iterShapeRecords():
        nom_departement_shape = shape_record.record[1]
        nom_departement_normalise = normaliser_nom_departement(nom_departement_shape)
        if nom_departement_normalise not in DEPARTEMENTS_A_EXCLURE_NORMALISES: 
            if nom_departement_normalise in dico_stat:
                dico_info_departement_filtre[nom_departement_shape] = [shape_record.shape.points , dico_stat[nom_departement_normalise][0] , shape_record.shape.bbox]
                DICO_SEGMENT[nom_departement_shape] = shape_record.shape.parts
    
    return dico_info_departement_filtre


def etape2_projection_mercator(dico_coord):
    dico_coord_mercator = {}
    x_min_all, x_max_all = float('inf'), float('-inf')
    y_min_all, y_max_all = float('inf'), float('-inf')
    for k, liste_info_dep in dico_coord.items(): 
        liste_points_deg = liste_info_dep[0] 
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

        x_min_mercator = math.radians(liste_info_dep[2][0])
        x_max_mercator = math.radians(liste_info_dep[2][2])
        y_min_mercator = math.log(math.tan((math.pi / 4) + (math.radians(liste_info_dep[2][1]) / 2))) 
        y_max_mercator = math.log(math.tan((math.pi / 4) + (math.radians(liste_info_dep[2][3]) / 2))) 

        pib_value = liste_info_dep[1]
        dico_coord_mercator[k] = [liste_coord_mercator, pib_value , [(x_min_mercator , y_min_mercator) , (x_max_mercator , y_max_mercator)]]
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
    for k, liste_mercator_info in dico_coord_mercator.items():
        liste_mercator = liste_mercator_info[0]
        pib_value = liste_mercator_info[1]
        bbox_mercator = liste_mercator_info[2]
        liste_coord_screen = []
        for lon_mercator, y_mercator in liste_mercator:
            vecteur_x_en_pixel = (lon_mercator - centre_x_mercator) * coefficient_ajustement
            vecteur_y_en_pixel = (y_mercator - centre_y_mercator) * coefficient_ajustement
            coordonnée_x_pixel = int(centre_fenetre_en_pixel + vecteur_x_en_pixel)
            coordonée_y_pixel = int(centre_fenetre_en_pixel - vecteur_y_en_pixel) 
            liste_coord_screen.append((coordonnée_x_pixel, coordonée_y_pixel))
        (x_min_merc, y_min_merc), (x_max_merc, y_max_merc) = bbox_mercator
        x_min_pix = int(centre_fenetre_en_pixel + (x_min_merc - centre_x_mercator) * coefficient_ajustement)
        x_max_pix = int(centre_fenetre_en_pixel + (x_max_merc - centre_x_mercator) * coefficient_ajustement)
        y_min_pix = int(centre_fenetre_en_pixel - (y_max_merc - centre_y_mercator) * coefficient_ajustement)
        y_max_pix = int(centre_fenetre_en_pixel - (y_min_merc - centre_y_mercator) * coefficient_ajustement)
        bbox_screen = [(x_min_pix, y_min_pix), (x_max_pix, y_max_pix)]
        
        dico_coord_screen[k] = [liste_coord_screen, pib_value, bbox_screen] 
    return dico_coord_screen


def etape3_5_calcul_indices(dico_coord_screen):
    liste_pib_entiers = []
    for liste_info in dico_coord_screen.values():
        try:
            pib_int = int(liste_info[1])
            liste_pib_entiers.append(pib_int)
        except ValueError:
            continue
    if not liste_pib_entiers:
        return dico_coord_screen
    max_pib = max(liste_pib_entiers)
    min_pib = min(liste_pib_entiers)
    amplitude_pib = max_pib - min_pib
    N = len(DEGRADE_COULEUR)
    for liste_info in dico_coord_screen.values():
        pib = int(liste_info[1])
        if amplitude_pib == 0:
            ratio = 0
        else:
            ratio = (pib - min_pib) / amplitude_pib
        indice_couleur = int(ratio * (N - 1))
        liste_info.append(indice_couleur) 
    return dico_coord_screen


def etape4_dessiner_carte(dico_coord_screen):
    fltk.cree_fenetre(FENETRE_TAILLE, FENETRE_TAILLE)
    for key , liste_info in dico_coord_screen.items() :
        if len(DICO_SEGMENT[key]) <= 1 :
            coordonnees_ecran = liste_info[0]
            indice_couleur = liste_info[3]
        
            couleur_remplissage = DEGRADE_COULEUR[indice_couleur]
            
            fltk.polygone(
                coordonnees_ecran, 
                couleur='black', 
                remplissage=couleur_remplissage,
                epaisseur=1
            )

        else : 
            coordonnees_ecran = liste_info[0]
            indice_couleur = liste_info[3]
            couleur_remplissage = DEGRADE_COULEUR[indice_couleur]
            zone = DICO_SEGMENT[key]
            for i in range(0 , len(zone)-1) : 
                
                fltk.polygone(
                coordonnees_ecran[zone[i]:zone[i+1]-1], 
                couleur='black', 
                remplissage=couleur_remplissage,
                epaisseur=1
            )
            fltk.polygone(
                coordonnees_ecran[zone[-1]:], 
                couleur='black', 
                remplissage=couleur_remplissage,
                epaisseur=1
            )
        for key , liste_info in dico_coord_screen.items() :
            x_cercle = (liste_info[2][1][0] + liste_info[2][0][0])/2
            y_cercle = (liste_info[2][1][1] + liste_info[2][0][1])/2
            fltk.cercle(x_cercle , y_cercle , FENETRE_TAILLE * 0.00300 , couleur="red" , remplissage="red") 
            COORDONEE_CENTRE_CERCLES[key] = [x_cercle , y_cercle]

        fltk.mise_a_jour()
            

def dessiner_pays(dico_stat) :
    dico_info_departement = etape1_chargement_et_filtrage(dico_stat)
    dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all = etape2_projection_mercator(dico_info_departement)
    dico_coord_screen = etape3_transformation_en_ecran(dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all)
    dico_coord_screen_colore = etape3_5_calcul_indices(dico_coord_screen) 
    etape4_dessiner_carte(dico_coord_screen_colore)


def dessiner_indicateur(dico_coord_screen_colore) :
    liste_pib_entiers = []
    for liste_info in dico_coord_screen_colore.values():
        try:
            pib_int = int(liste_info[1]) 
            liste_pib_entiers.append(pib_int)
        except ValueError:
            continue
    if not liste_pib_entiers:
        return 
    min_pib = min(liste_pib_entiers)
    max_pib = max(liste_pib_entiers)
    amplitude_indicateur = max_pib - min_pib
    i = 0
    N = len(DEGRADE_COULEUR)
    hauteur_rectangle = FENETRE_TAILLE // N 
    bord_1_x = FENETRE_TAILLE * 0.98
    bord_1_y = 0
    bord_2_x = FENETRE_TAILLE
    valeur_par_indice = amplitude_indicateur / (N - 1) 
    for rectangle in range(0, N):
        fltk.rectangle(bord_1_x, bord_1_y , bord_2_x , bord_1_y + hauteur_rectangle , remplissage = DEGRADE_COULEUR[i])
        if i % 5 == 0:
            valeur_affichee = int(min_pib + (i * valeur_par_indice)) 
            fltk.texte(bord_1_x - round(FENETRE_TAILLE * 0.045) , bord_1_y, str(valeur_affichee), couleur="black", taille=round(FENETRE_TAILLE * 0.015))
        bord_1_y += hauteur_rectangle
        i += 1
    if (N - 1) % 5 != 0:
        fltk.texte(bord_1_x - round(FENETRE_TAILLE * 0.045) , FENETRE_TAILLE - 20, str(max_pib), couleur="black", taille=round(FENETRE_TAILLE * 0.015))


def dessiner_pays(dico_stat) :
    dico_info_departement = etape1_chargement_et_filtrage(dico_stat)
    dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all = etape2_projection_mercator(dico_info_departement)
    dico_coord_screen = etape3_transformation_en_ecran(dico_coord_mercator, x_min_all, x_max_all, y_min_all, y_max_all)
    dico_coord_screen_colore = etape3_5_calcul_indices(dico_coord_screen) 
    etape4_dessiner_carte(dico_coord_screen_colore)
    return dico_coord_screen_colore

def dessiner_zone_info() :
    fltk.rectangle(0 , 0 , FENETRE_TAILLE * 0.20 , FENETRE_TAILLE * 0.20)

def afficher_info(x_clic , y_clic , dico_coord_screen_colore) :
    for key , coordonee in COORDONEE_CENTRE_CERCLES.items() :
        result_x = abs(x_clic - coordonee[0])
        result_y = abs(y_clic - coordonee[1])
        if (result_x <= FENETRE_TAILLE * 0.00300) and (result_y <= FENETRE_TAILLE * 0.00300) :
            fltk.texte(FENETRE_TAILLE * 0.00750 , FENETRE_TAILLE * 0.00750 , key , taille=round(FENETRE_TAILLE * 0.015) , tag="bonjour")
            fltk.texte(FENETRE_TAILLE * 0.00750 , FENETRE_TAILLE * 0.1 , dico_coord_screen_colore[key][1] , taille=round(FENETRE_TAILLE * 0.015) , tag = "Toto")
def main():
    info = recuperer_csv("Pib_par_habitant.csv")
    dico_colore = dessiner_pays(info)
    dessiner_indicateur(dico_colore)
    dessiner_zone_info()
    while True:
        ev = fltk.donne_ev()
        tev = fltk.type_ev(ev)

        if tev == "ClicGauche":
            print("Clic gauche au point", (fltk.abscisse(ev), fltk.ordonnee(ev)))
            fltk.efface("bonjour")
            fltk.efface("Toto")
            afficher_info(fltk.abscisse(ev) , fltk.ordonnee(ev) , dico_colore)
        elif tev == 'Quitte':
            break

        else:
            pass

        fltk.mise_a_jour()

    fltk.ferme_fenetre()



main()