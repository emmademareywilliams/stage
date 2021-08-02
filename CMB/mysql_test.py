import mysql.connector

# on décide si on veut écrire ou lire le flux :
wr = True
feedId = 25

try:
    connection = mysql.connector.connect(host='localhost',database='emoncms',user='emoncms',password='emonpiemoncmsmysql2016')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        message = "Connected to MySQL Server version {} :-)\n".format(db_Info)
        print(message)
        # on utilise l'option dictionnary pour avoir un retour similaire à celui de fetch_object() en PHP
        cursor = connection.cursor(dictionary=True)
except Error as e:
    message = "Error while connecting to MySQL {}".format(e)
finally:
    if connection.is_connected():
        if wr:
            # on veut écrire --> 2 possibilités :
            #   - le flux n'existe pas, donc on le crée
            #   - le flux existe déjà, donc on le met à jour
            query = 'INSERT INTO feeds(datatype,engine,name,public,userid,tag)VALUES(1,5,"pompe","",1,"pompe_fonct")'
            #query = 'UPDATE feeds SET engine=5 WHERE id={}'.format(feedId)
            cursor.execute(query)
            print(query)
            query_nb = 'SELECT * FROM feeds'
            cursor.execute(query_nb)
            records = cursor.fetchall()
            print(records)
        else :
            #query = 'SELECT * FROM feeds where id={}'.format(feedId)
            #query = "DELETE from feeds where id=27"
            #cursor.execute(query)

            query = 'SELECT * from feeds'
            cursor.execute(query)
            records = cursor.fetchall()
            print(records)



# structure du dictionnaire de feeds :
# [{'id': 1, 'name': 'VAN_Text', 'userid': 1, 'tag': 'sofrel_Vantage', 'time': None, 'value': None,
# 'datatype': 1, 'public': 0, 'size': 17662216, 'engine': 5, 'server': 0, 'processList': None, 'unit': ''}]
# id,name,userid,tag,time,value,datatype,public,size,engine,server,processList,unit
