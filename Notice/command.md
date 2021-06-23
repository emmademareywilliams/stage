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

Pour gérer les systèmes et services de la machines :
```
system ctl start --> démarre le service 
system ctl stop --> arrête le service 
```

Pour se placer comme super utilisateur :
```
sudo 
```

Pour avoir accès au journal d’un certain service (aka tout ce qu’il a fait depuis un certain temps) :
```
journal ctl 
```

> Cette ligne de commande, qui peut être assimilée à un log, est pratique lorsqu'il s'agit de débugger un programme.


Pour créer un nouveau fichier :
```
touch {nom du fichier}.{extension}
```

Pour changer le groupe d'un fichier :
```
chown 
```

> Le niveau d'autorisation d'un fichier change en fonction du groupe : par exemple, pour un fichier donné, le propriétaire peut lire et écrire dans ce fichier, alors que le groupe n'a que la possibilité de le lire. 

Pour changer le mode d'un fichier (exécutable ou non) : 
```
chmod 
```

Pour effacer un fichier :
```
rm
```



