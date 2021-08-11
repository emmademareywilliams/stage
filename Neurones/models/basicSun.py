"""
a very basic sun model
"""
import math

def deltaT(n,hour=True):
    """
    n : numéro du jour de l'année - 1er janvier = jour 1
    valeur de l'équation du temps pour le jour n de l'année
    équation dite de Duffie et Beckman
    résultat en heures ou minutes
    """
    B=2*math.pi*(n-1)/365
    E=229.2*(0.000075+0.001868*math.cos(B)-0.032077*math.sin(B)-0.014615*math.cos(2*B)-0.04089*math.sin(2*B))
    if hour==True:
        return E/60
    else:
        return E

def earthDeclination(n,rad=True):
    """
    n : numéro du jour de l'année - 1er janvier = jour 1
    déclinaison solaire
    angle formé par la direction du soleil et le plan équatorial terrestre
    cet angle varie au cours des saisons
    resultat en degrés ou radians
    """
    ed=23.45*math.sin(2*math.pi*(284+n)/365)
    if rad==True:
        return math.radians(ed)
    else:
        return ed

def hourAngle(n,hu,lon,rad=True):
    """
    n : numéro du jour de l'année - 1er janvier = jour 1
    hu : heure UTC
    lon : longitude en degré
    angle horaire
    à chaque heure qui s'écoule correspond une augmentation de l'angle horaire de 15°
    """
    w = 15*(hu+deltaT(n)-12) + lon

    if rad==True:
        return math.radians(w)
    else:
        return w

def solarAngles(n,hu,radlat,lon,rad=True):
    """
    n : numéro du jour de l'année - 1er janvier = jour 1
    hu : heure UTC
    lon : longitude en degré
    radlat: latitude en radian
    calcule les angles solaires :
    - (gamma)hauteur angulaire du soleil = angle formé par le plan horizontal et la direction du soleil
    - (alpha)azimuth = angle entre le méridien du lieu et le plan vertical passant par le soleil
    resultats en degrés ou radians
    """
    decl=earthDeclination(n)
    w=hourAngle(n,hu,lon)
    #hauteur du soleil - sun height : sh
    sh = math.sin(radlat)*math.sin(decl) + math.cos(radlat)*math.cos(decl)*math.cos(w)
    gamma=math.asin(sh)
    #trace du soleil dans le plan horizontal
    alpha=math.asin(math.cos(decl)*math.sin(w)/math.cos(gamma))
    if gamma < 0:
        gamma=0

    if rad==True:
        return gamma, alpha, w
    else:
        return math.degrees(gamma), math.degrees(alpha), math.degrees(w)

def Linke(n,radlat,z,gamma):
    """
    n : numéro du jour de l'année - 1er janvier = jour 1
    hu : heure UTC
    lon : longitude en degré
    radlat: latitude en radian
    z: altitude en kilomètre
    pour trouver facilement l'altitude d'un point
    https://www.daftlogic.com/sandbox-google-maps-find-altitude.htm
    modèle de Capderou du trouble de Linke par temps clair
    du à l'absorption par les gaz de l'atmosphère (02, CO2, O3 ozone, water vapor, aerosols)
    """
    sinphi = math.sin(radlat)
    # variation saisonnière
    A=math.sin(2*math.pi*(n-121)/365)
    T1 = 2.4 - 0.9*sinphi + 0.1*(2 + sinphi)*A - 0.2*z - (1.22+0.14*A)*(1-math.sin(gamma))
    T2 = 0.89**z
    T3 = (0.9 + 0.4*A)*0.63**z
    return T1+T2+T3

def globalRadiation(n,hu,lat,lon,alt):
    """
    radiation globale par temps clair en W/m2
    cf OMM
    https://hal.archives-ouvertes.fr/jpa-00246138/document
    """
    radlat=math.radians(lat)
    gamma = solarAngles(n,hu,radlat,lon)[0]
    z=alt/1000
    TL = Linke(n,radlat,z,gamma)
    mod = (1300-57*TL)*math.exp(0.22*z/7.8)*math.sin(gamma)**((TL+36)/33)
    return mod

def Kc(neb):
    """
    cloud attenuation factor (Kc) défini par Kasten and Czeplak (1980)
    """
    return 1-0.75*(neb/100)**3.4
