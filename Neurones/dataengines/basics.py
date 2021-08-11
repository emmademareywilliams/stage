import numpy as np

def samplingts(data,step):
    """
    fonction de ré-échantillonnage sur timeserie à pas variable
    data : matrice des données originales
    colonne 0 : unix timestamp en secondes
    colonne 1 : nébulosité en % / radiation solaire glob. en W/m2
    colonne 2 : température en °C
    colonne 3 : température ressentie en °C
    step : pas de temps à utiliser pour le rééchantillonnage
    return : sampled = matrice des données ré-échantillonnées
    """
    n = data.shape[0]-1
    nf = data.shape[1]
    xr = np.arange(data[0,0] ,data[-1,0] ,step)
    nb = xr.shape[0]
    sampled = np.zeros((nb,nf))
    sampled[:,0] = xr
    j=0
    for i in range(n):
        interval = data[i+1,0]-data[i,0]
        slices = int(interval // step)
        #print("interval is {} - {} slices".format(interval,slices))
        delta=np.zeros(nf)
        for k in range(1,nf):
            delta[k] = ( data[i+1,k] - data[i,k] ) / slices
        for index in range(slices):
            if index==0:
                for k in range(1,nf):
                    sampled[j,k]=data[i,k]
            else:
                for k in range(1,nf):
                    sampled[j,k]=sampled[j-1,k]+delta[k]
            j+=1
    return sampled
