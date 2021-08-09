import time
import math
import struct
import numpy as np
import os.path
import redis
import mysql.connector

# if want to work on the active directory, just use dir="."
dir="/var/opt/emoncms/phpfina"

"""
Some functions to create a new PHPFina feed
"""

def getMetas(nb,dir=dir):
    """
    read meta given a feed number
    print (interval,starting timestamp)
    """
    f=open("{}/{}.meta".format(dir,nb),"rb")
    f.seek(8,0)
    hexa = f.read(8)
    aa= bytearray(hexa)
    if len(aa)==8:
      decoded=struct.unpack('<2I', aa)
    print(decoded)
    f.close()
    return decoded


def createFeed(nb,data,dir=dir):
    """
    create a dat file given :
    - a feed number
    - a numpy vector of data
    """
    f=open("{}/{}.dat".format(dir,nb),"wb")
    format="<{}".format("f"*len(data))
    bin=struct.pack(format,*data)
    f.write(bin)
    f.close()


def createMeta(nb,start,step,dir=dir):
    """
    create meta given :
    - a feed number
    - a unixtimestamp as start
    - a step
    """
    f=open("{}/{}.meta".format(dir,nb),"wb")
    data=np.array([0,0,step,start])
    format="<{}".format("I"*len(data))
    bin=struct.pack(format,*data)
    f.write(bin)
    f.close()


def newPHPFina(nb,start,step,data,dir=dir):
    """
    create a PHPFina object, without any reference to any EmonCMS server
    start : unix time stamp of the starting point
    step : timestep/interval in s
    data : data to be injected as a numpy vector
    """
    meta="{}/{}.meta".format(dir,nb)
    if os.path.isfile(meta) and os.path.getsize(meta) != 0:
        print("meta file exists")
        getMetas(nb,dir)
    else:
        print("creating meta")
        createMeta(nb,start,step,dir)
    if os.path.isfile("{}/{}.dat".format(dir,nb)):
        print("data file exists")
    else:
        print("creating data file")
        createFeed(nb,data,dir)


"""
Creation of the initial numpy array corresponding to the pump operation:
"""

def newFeed(refFeed, newNb):
    """
    creates a new PHPFina blank feed (.dat and .meta files)
    refFeed: number (int) of the reference feed (used to get the interval and the starting time)
    newNb: number (int) of the new feed
    """
    interval, starttime = getMetas(refFeed)
    now = time.time()
    duration = now - starttime
    nb_pts = int(duration / interval)
    data = np.ones(nb_pts)
    newPHPFina(newNb, starttime, interval, data, dir)



def newFeedEmoncms(refFeed, name, tag, verif=False):
    """
    creates the new feed and inserts it into EmonCMS
    refFeed: number (int) of the reference feed
    name: string, name of the feed
    tag: string, tag for the feed
    """

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
            """
            insertion of the new feed into the SQL database:
            """
            query = 'INSERT INTO feeds(datatype,engine,name,public,userid,tag)VALUES(1,5,"{}","",1,"{}")'.format(name, tag)
            cursor.execute(query)

            """
            the feed number is retrieved so that the associated .dat and .meta files can be created:
            """
            query = 'SELECT MAX(id) FROM feeds'
            cursor.execute(query)
            newNb = int(cursor.fetchall()[0]['MAX(id)'])
            print(newNb)
            newFeed(refFeed, newNb)

            """
            Redis is reset so that the new feed can be recognised by Emoncms
            """
            r = redis.Redis(host='localhost', port=6379, db=0) # db = database number
            r.flushdb()  # Flush database: clear old entries

            if verif:
                query = "SELECT * from feeds"
                cursor.execute(query)
                records = cursor.fetchall()
                print(records)


newFeedEmoncms(1, "test", "Test_newfeed", verif=True)
