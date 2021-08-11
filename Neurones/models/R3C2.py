"""
modèle R3C2 pour une zone de bâtiment
"""
import numpy as np

def MatriX(p,jac=True):
    """
    The RC matrix associated to a R3C2 electric model of a Building

    CRES: thermal capacity of the indoor (the air inside the building)

    CS: thermal capacity of the envelope

    RI: thermal resistance between the envelope and the indoor (wall internal resistance)

    R0: thermal resistance between the envelope and the outdoor (wall external resistance)

    RF: thermal resistance due to air leakage
    """
    #print(p)
    CRES=p[0]
    CS=p[1]
    RI=p[2]
    R0=p[3]
    RF=p[4]
    A=np.array([ [-1/CRES*(1/RI+1/RF), 1/(CRES*RI)      ],
                 [1/(CS*RI)          , -1/CS*(1/RI+1/R0)] ])

    B=np.array([ [1/(CRES*RF), 1/CRES, 0   ],
                 [1/(CS*R0)  , 0     , 1/CS] ])

    if jac :
        dA=[]
        dA.append(np.array([ [(1/RI+1/RF)/CRES**2, -1/(RI*CRES**2)], [0            ,  0                ] ]))
        dA.append(np.array([ [0                  ,  0             ], [-1/(RI*CS**2), (1/RI+1/R0)/CS**2 ] ]))
        dA.append(np.array([ [1/(CRES*RI**2)     , -1/(CRES*RI**2)], [-1/(CS*RI**2), 1/(CS*RI**2)      ] ]))
        dA.append(np.array([ [0                  , 0              ], [0            , 1/(CS*R0**2)      ] ]))
        dA.append(np.array([ [1/(CRES*RF**2)     , 0              ], [0            , 0                 ] ]))

        dB=[]
        dB.append(np.array([ [-1/(RF*CRES**2), -1/CRES**2, 0], [0            , 0, 0          ] ]))
        dB.append(np.array([ [0              , 0         , 0], [-1/(R0*CS**2), 0, -1/(CS**2) ] ]))
        dB.append(np.array([ [0              , 0         , 0], [0            , 0, 0          ] ]))
        dB.append(np.array([ [0              , 0         , 0], [-1/(CS*R0**2), 0, 0          ] ]))
        dB.append(np.array([ [-1/(CRES*RF**2), 0         , 0], [0            , 0, 0          ] ]))

    if jac :
        return A, B, dA, dB
    else :
        return A, B

def Ts(ti,te):
    """
    evaluate the envelope temperature given indoor and outdoor temperature

    ONLY USED AS A STARTING POINT

    simulation outputs indoor AND envelope temperatures
    """
    return (ti+2*te)/3


class R3C2Zone:
    """
    modélise une zone de bâtiment chauffée par un circuit unique sous la forme d'un circuit R3C2

    Notations et unités

    Text : température extérieure, Phea : puissance de chauffage, Sun: rayonnement solaire

    Puissances exprimées en W et températures exprimées en °C

    """
    def __init__(self,step,p):
        A, B = MatriX(p,jac=False)
        n=A.shape[0]
        AS_B=np.linalg.inv(np.eye(n)-step*A/2)
        AS_C=AS_B.dot(np.eye(n)+step*A/2)
        AS_B=step*AS_B/2
        self.A=A
        self.B=B
        self.n=n
        self.AS_B=AS_B
        self.AS_C=AS_C
        self.step=step

    def predict_Euler(self, x0, inputs):
        """
        prédit les conditions intérieures en utilisant le schéma d'Euler

        2 cas de figure :
        1) un unique point à prévoir
        2) plusieurs points à prévoir

        Cas 1)

        inputs : np.array(3) = [ Text(s), Phea(s), Sun(s) ]

        x0     : np.array(2) = [ Tint(s), Tsurface(s) ]

        output : np.array(2) = [ Tint(s+1), Tsurface(s+1) ]


        Cas 2)

        inputs : np.array(n,3) = [[ Text, Phea, Sun ]]

        x0     : np.array(2) = [ Tint0, Tsurface0 ]

        output : np.array(n,2) = [[ Tint, Tsurface ]]

        """
        # only one point to predict
        if inputs.shape == (inputs.shape[0],):
            x = np.linalg.inv(np.eye(self.n)-self.step*self.A).dot(x0+self.step*self.B.dot(inputs))
        # more than one point to predict
        else:
            nbpts=inputs.shape[0]
            x = np.zeros((nbpts, self.n))
            x[0] = x0
            for i in range(nbpts-1):
                x[i+1] = np.linalg.inv(np.eye(self.n)-self.step*self.A).dot(x[i]+self.step*self.B.dot(inputs[i]))

        return x

    def predict_Krank(self, x0, inputs):
        """
        prédit les conditions intérieures en utilisant le schéma de Krank Nicholson

        inputs : tenseur des sollicitations

        x0 : vecteur numpy des conditions initiales [Tint0, Ts0]

        Tint0 est le température intérieure initiale, Ts0 la température de surface initiale

        inputs : np.array(n,3) = [[ Text, Phea, Sun ]]

        sortie : tenseur x de taille (n+1,2)

        x[1:,0] : n prédiction(s) de température intérieure en °C

        x[1;,1] : n prédiction(s) de température de surface en °C

        si l'on veut prédire un seul point, il faut donner un tenseur des sollicitations de taille (2,3)

        si l'on veut prédire n points, il faut donner un tenseur des soliicitations de taille (n+1,3)

        """
        nbpts=inputs.shape[0]
        x=np.zeros((nbpts,self.n))
        x[0] = x0

        for i in range(nbpts-1):
            x[i+1]=self.AS_C.dot(x[i])+self.AS_B.dot(self.B.dot(inputs[i+1]+inputs[i]))

        # on pourrait retourner x[1:,:] si on voulait ne retourner que les n prédictions
        return x
