# Liste des commandes couramment utilisées dans un terminal Linux 

Pour installer des packages Python : 
```
pip install 
```

Pour se déplacer de répertoire en répertoire :
```
cd 
```

Pour lancer l'exécution du fichier Python correspondant :
```
python3 {nom du fichier}.py
```

Pour avoir accès à toutes les données des tâches en cours d'exécution (% de CPU, % de MEM, etc.) :
```
top
```

Pour se placer comme super utilisateur :
```
sudo 
```

Pour gérer les systèmes et services de la machines :
```
sudo systemctl start {nom du service} --> démarre le service 
sudo systemctl stop {nom du service} --> arrête le service 
```


Pour avoir accès au journal d’un certain service (aka tout ce qu’il a fait depuis un certain temps) :
```
sudo journalctl {nom du service} -u -f 
```

> Cette ligne de commande, qui peut être assimilée à un log, est pratique lorsqu'il s'agit de débugger un programme.


Pour créer un nouveau fichier :
```
touch {nom du fichier}.{extension}
```

Pour changer le groupe d'un fichier :
```
chown 
OU
chgrp --> plus simple d'utilisation 
```

> Le niveau d'autorisation d'un fichier change en fonction du groupe : par exemple, pour un fichier donné, le propriétaire peut lire et écrire dans ce fichier, alors que le groupe n'a que la possibilité de le lire. 

Pour changer le mode d'un fichier (exécutable ou non) : 
```
chmod 
```
Cette commande peut être suivie par les instructions suivantes : 
* `+/- {niveau}`: pour changer le niveau d'interaction du groupe avec le fichier 
* `666`: tous les utilisateurs peuvent lire et écrire, mais pas exécuter 
* `777`: tous les utilisateurs peuvent effectuer toutes les actions possibles sur les fichiers (y compris l'exécution) 

> Les différents niveaux d'interaction d'un utilisateur avec les fichiers sont les suivants : 
> - `r` = read 
> - `w` = write
> - `x` = execute 


Pour effacer un fichier :
```
rm
```

Pour copier des fichiers et/ou répertoires :
```
cp
```

Pour créer un répertoire : 
```
mkdir
```

Pour créer des liens / raccourcis entre différents fichiers : 
```
ln
```

Pour lister tous les fichiers contenus dans le répertoire courant :
```
ls 
```

> Cette commande peut être suivie de `-l` afin d'avoir accès aux autorisations accordées aux différents groupes pour chacun des fichiers. 
