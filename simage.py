#!/usr/bin/python
import os
import sqlite3 as lite
import time
import shutil
import tarfile
import sys, getopt
import PIL
import imghdr
import mimetypes
import hashlib
from PIL import Image
import logging


##################################################
# Modify the following variables to point to the #
# rigth path.                                    #
##################################################

##/   Windows enviroment /##

#WORKINGPATH = 'F:\Python\awaio'

##/   Linux enviroment /##

WORKINGPATH = '/run/media/raguayo/0df984f7-e39e-4723-b946-96df59c9e5a1/Fotos/'     # Directory where the pictures are going tobe sorted
DATABASE = WORKINGPATH + 'ArchiveDatabase.db'                                             # Database to keep track of changes
PICTUREDIR='/run/media/raguayo/90d270f3-f668-4323-b5bc-35dee22060fd/pub/FotosOri/'      # Directory keeping original pictures



##################################################
# This is Class definition sections              #
#                                                #
##################################################

class TimeStampClass:
    Count = 0
    def __init__(self,Time):
        self.Time = Time
        TimeStampClass.Day = Time[8:10]
        TimeStampClass.Month = Time[5:7]
        TimeStampClass.Year = Time[0:4]
        TimeStampClass.Hour = Time[11:13]
        TimeStampClass.Minute = Time[14:16]
        TimeStampClass.Second = Time[17:19]
        TimeStampClass.TimeFormated = Time[0:4] + '-' + Time[4:6] + '-' + Time[6:8] + ' ' + Time[8:10] + ':' + Time[10:12]
        TimeStampClass.Count += 1

class EXIFClass:
    Count = 0
    def __init__(self,OriginalDir,OriginalName,FileType,Date,Brand,Model,UUID, MD5):
        self.OriginalDir = OriginalDir
        self.OriginalName = OriginalName
        self.Date = TimeStampClass(Date)
        self.Brand = Brand
        self.Model = Model
        self.UUID = UUID
        self.MD5 = MD5
        EXIFClass.Info = True
        EXIFClass.Count += 1        
        EXIFClass.NewName = TimeStampClass(Date).Year + TimeStampClass(Date).Month + TimeStampClass(Date).Day + '_' + \
                            TimeStampClass(Date).Hour + TimeStampClass(Date).Minute + TimeStampClass(Date).Second + Brand[0] + Model[0] + str(EXIFClass.Count).zfill(4)
        

class VIDEOClass:
    Count = 0
    ModifyTime = ""
    StringTime = ""

    def __init__(self,OriginalDir,OriginalName,FileType,Info, MD5):
        self.OriginalDir = OriginalDir
        self.OriginalName = OriginalName
        self.FileMetadata = os.stat(OriginalDir + '/' + OriginalName)
        self.Brand = 'No Brand'
        self.Model = 'No Model'
        self.UUID = 1
        self.Info = Info
        self.MD5 = MD5
        
        VIDEOClass.ModifyTime = time.localtime(os.stat(OriginalDir + '/' + OriginalName).st_mtime)
        VIDEOClass.StringTime = str(VIDEOClass.ModifyTime.tm_year).zfill(4) + ":" + str(VIDEOClass.ModifyTime.tm_mon).zfill(2) + ":" + \
                                str(VIDEOClass.ModifyTime.tm_mday).zfill(2) + ':' + str(VIDEOClass.ModifyTime.tm_hour).zfill(2) + ":" + \
                                str(VIDEOClass.ModifyTime.tm_min).zfill(2) +  ':' + str(VIDEOClass.ModifyTime.tm_sec).zfill(2) 
        VIDEOClass.Date = TimeStampClass(VIDEOClass.StringTime)
        VIDEOClass.Count += 1        
        VIDEOClass.NewName = VIDEOClass.Date.Year + VIDEOClass.Date.Month + VIDEOClass.Date.Day + '_' + VIDEOClass.Date.Hour + VIDEOClass.Date.Minute + VIDEOClass.Date.Second + str(VIDEOClass.Count).zfill(4)

class OTHERClass:
    Count = 0
    ModifyTime = ""
    StringTime = ""

    def __init__(self,OriginalDir,OriginalName,FileType,MD5):
        self.OriginalDir = OriginalDir
        self.OriginalName = OriginalName
        self.FileMetadata = os.stat(OriginalDir + '/' + OriginalName)
        self.MD5 = MD5
        OTHERClass.ModifyTime = time.localtime(os.stat(OriginalDir + '/' + OriginalName).st_mtime)
        OTHERClass.StringTime = str(OTHERClass.ModifyTime.tm_year).zfill(4) + ":" + str(OTHERClass.ModifyTime.tm_mon).zfill(2) + ":" + \
                                str(OTHERClass.ModifyTime.tm_mday).zfill(2) + ':' + str(OTHERClass.ModifyTime.tm_hour).zfill(2) + ":" + \
                                str(OTHERClass.ModifyTime.tm_min).zfill(2) +  ':' + str(OTHERClass.ModifyTime.tm_sec).zfill(2) 
        OTHERClass.Date = TimeStampClass(OTHERClass.StringTime)
                

        OTHERClass.Info = True
        OTHERClass.Count += 1
        OTHERClass.NewName = OriginalName


#       0123456789012345    
#       2015-02-17 20:15:00+10:00

##################################################
# This is Functions definition sections          #
#                                                #
###############################################@crakaman ###

#Generate MD5 fingerprint (for the files
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def program_logic(line):
    global line_count
    line_count += 1
#   print (str(line_count) + ': ' + line.rstrip()


def print_help():
    print ('Usage: exmplae.py -h')
    print ('        this help')

def Connect_Databases(DATABASE):
        global DBConnection
        global DBCursor
        
        try:
            print ('connecting to database')
            DBConnection = lite.connect(DATABASE)        #create the connection to the data base
            print ("connection stablished\nCreating Cursor")
            DBCursor = DBConnection.cursor() 
            print ("Cursor created")
        
        except (lite.Error, e):
            print ("connection failed")
            print ("Error %s" % e.args[0])


def Create_Database(): 
        DBCursor.executescript("""
        CREATE TABLE IF NOT EXISTS Garbage(Id INTEGER PRIMARY KEY, Name TEXT, OldName TEXT, Path TEXT, OldPath TEXT, 
                                         Type TEXT, Taken DATE, Created DATE, Brand TEXT, Model TEXT, Result TEXT, MD5 TEXT);
        CREATE TABLE IF NOT EXISTS Files(Id INTEGER PRIMARY KEY, Name TEXT, Path TEXT, Type TEXT, Taken DATE, Created DATE, 
                                         Brand TEXT, Model TEXT, Result TEXT, MD5 TEXT);
        CREATE TABLE IF NOT EXISTS Migration(Id INTEGER PRIMARY KEY, Name TEXT, OldName TEXT, Path TEXT, OldPath TEXT, 
                                         Type TEXT, Taken DATE, Created DATE, Brand TEXT, Model TEXT, Result TEXT, MD5 TEXT);
        
        """)
        DBConnection.commit()



#---------------- Main Program ----------------#


if __name__ == "__main__":
        
    
    PICTUREDIR     
    WORKINGPATH
    Archivos = []
    Count = -1
    GarbageCount = 0
    VideoCount = 0
    logging.basicConfig(filename='/tmp/simage.log',level=logging.DEBUG)

    # if doesnt exist create new database structure and output directory. 
    if not(os.path.exists(WORKINGPATH)):  
        os.mkdir(WORKINGPATH)
            
    if os.path.exists(DATABASE):
        Connect_Databases(DATABASE)
    else:
        Connect_Databases(DATABASE)
        Create_Database()
        print ('New database created')

    #Use the first argument given as the location of the originals to be added to the archive
    try: 
        PICTUREDIR = sys.argv[1]
        os.chdir(PICTUREDIR)
    except:
        print (PICTUREDIR + " can't be accesed, please input the rigth directory with the originals")
        print ("example: pyhton simage.py /directory/")
        sys.exit()
        

    #Walk the entire directory three to find new files
    for dirname, dirnames, filenames in os.walk(PICTUREDIR):                       
        for filename in filenames:
#           if filename.endswith('.JPG') or filename.endswith('.jpg')  :                        
            ImageType =imghdr.what(dirname + '/' + filename)
            FileType = mimetypes.guess_type(dirname + '/' + filename, strict=False)[0]
            logging.debug(FileType)
            #if ImageType != None and ImageType != 'png':
            #Count +=1
            logging.info ('Processing ' + filename)
            Signature = md5(dirname + '/' + filename)
            logging.debug("file signature" + Signature)
            Query = "SELECT Id FROM Files WHERE MD5 = '" + Signature + "';"
            logging.debug ("searching for file signature in database \t"  + Query)
            DBCursor.execute(Query)
            Exist = DBCursor.fetchone()
            logging.debug ("Search result :")
            logging.debug (Exist)
            if Exist == None:    
            
                if FileType == None:        #Routines to separate files that are not images or videos and send them to the garbage directory
                    try:
                        os.mkdir(WORKINGPATH + 'garbage')
                    except:
                        pass
                    #print ('Coping ' + dirname + '/' + filename,WORKINGPATH + 'garbage/' + filename)
                    Archivos.append(OTHERClass(dirname,filename,FileType,md5(dirname + '/' + filename)))
                    Count +=1
                    shutil.copy2(dirname + '/' + filename,WORKINGPATH + 'garbage/' + str(GarbageCount) + filename )
                    GarbageCount = GarbageCount + 1
                    Query =  "INSERT INTO Garbage (Name, OldName, Path, OldPath, Type, Taken, Created, Brand, Model, Result, MD5) \
                              VALUES('" + \
                              str(GarbageCount) + filename + "', '" + \
                              filename + "','" + \
                              WORKINGPATH + "garbage/','" + \
                              dirname + "','" + \
                               "','','','','','Ok','" + \
                                md5(dirname + '/' + filename) +"')"
                    #print (Query )
                    DBCursor.execute(Query)
                    DBConnection.commit()
                    
    
                else:               # Open the files to extract metadata 
                    if FileType[0:5] == 'image' and FileType[6:9] != 'png':
                        #print ('For image ' + dirname + '/' + filename + '   ' + FileType[6:9])
                        im = PIL.Image.open(dirname + '/' + filename)
                        try:
                            exifdata = im._getexif()
                            Archivos.append(EXIFClass(dirname,filename,FileType,exifdata[0x9003][0],exifdata[0x010f],exifdata[0x0110],1, \
                                            md5(dirname + '/' + filename)))
                            Count +=1
                            #print ('\t' + exifdata[0x9003][0] #date)
                            #print ('\t' + exifdata[0x010f][0] #Brand)
                            #print ('\t' + exifdata[0x0110][0] #Model)
                        except:
                            Archivos.append(VIDEOClass(dirname,filename,FileType,False,md5(dirname + '/' + filename)))
                            Count +=1
                            #print (Archivos[Count].NewName + os.path.splitext(filename)[1])
                        #print (Archivos[Count].Date.Year)
                        #if not(os.path.exists(WORKINGPATH + PictureTaken.Year)):
                    elif FileType[0:5] == 'video':
                        #Count +=1
                        Archivos.append(VIDEOClass(dirname,filename,FileType,True,md5(dirname + '/' + filename)))                 
                        Count +=1
                        #print ('video name ' + Archivos[Count].NewName)
                    elif FileType[0:5] == 'audio':
                        #Count +=1
                        Archivos.append(VIDEOClass(dirname,filename,FileType,True,md5(dirname + '/' + filename)))                 
                        Count +=1
                    
                    else:
                        print ('Not image/video info ' + filename + '   ' + FileType)
                        shutil.copy2(dirname + '/' + filename,WORKINGPATH + 'garbage/' + str(GarbageCount) + filename )
                        Query =  "INSERT INTO Garbage (Name, OldName, Path, OldPath, Type, Taken, Created, Brand, Model, Result, MD5) \
                                VALUES('" + \
                                str(GarbageCount) + filename + "', '" + \
                                filename + "','" + \
                                WORKINGPATH + "garbage/','" + \
                                dirname + "','" + \
                                FileType + "','','','','','Ok','" + md5(dirname + '/' + filename) +  "')"
                        #print (Query )
                        DBCursor.execute(Query)
                            
                    
                    if Archivos[Count].Info :
                        try:
                            os.mkdir(WORKINGPATH + Archivos[Count].Date.Year)
                        except:
                            pass
                        try:
                            os.mkdir(WORKINGPATH + Archivos[Count].Date.Year + '/' + Archivos[Count].Date.Month)
                        except:
                            pass
                        try:
                            shutil.copy2(dirname + '/' + filename,WORKINGPATH + Archivos[Count].Date.Year + '/' \
                            + Archivos[Count].Date.Month + '/' + Archivos[Count].NewName + os.path.splitext(filename)[1])
                            Query =  "INSERT INTO Files (Name, Path, Type, Taken, Created, Brand, Model, Result,MD5) \
                                VALUES('" + \
                                Archivos[Count].NewName + os.path.splitext(filename)[1] + "', '" + \
                                WORKINGPATH + Archivos[Count].Date.Year + "/" + Archivos[Count].Date.Month + "/','" + \
                                FileType + "','','','','','Ok','" + md5(dirname + '/' + filename) +  "')"
                            #print (Query) 
                            DBCursor.execute(Query)
                        

                           #print ('Coping  ' + filename + ' to ' + WORKINGPATH + Archivos[Count].Date.Year + '/' + Archivos[Count].Date.Month + \
                           #      '/' + Archivos[Count].NewName + os.path.splitext(filename)[1])
                           #print()
                        except:
                            print ('failed copy of ' + dirname + '/' + filename )
                            Query =  "INSERT INTO Files (Name, Path, Type, Taken, Created, Brand, Model, Result, MD5) \
                                VALUES('" + \
                                Archivos[Count].NewName + os.path.splitext(filename)[1] + "', '" + \
                                WORKINGPATH + Archivos[Count].Date.Year + "/" + Archivos[Count].Date.Month + "/','" + \
                                FileType + "','','','','','Fail',,'')"
                            #print (Query )
                            DBCursor.execute(Query)
                           
                    else:
                        try:
                            os.mkdir(WORKINGPATH + '0000')
                        except:
                            pass
                        try:
                           shutil.copy2(dirname + '/' + filename , WORKINGPATH + '0000/' + Archivos[Count].NewName + os.path.splitext(filename)[1])
                           #print ('Coping  ' + filename + ' to ' + WORKINGPATH + '0000/' + Archivos[Count].NewName + os.path.splitext(filename)[1])
                           Query =  "INSERT INTO Files (Name, Path, Type, Taken, Created, Brand, Model, Result, MD5) \
                                VALUES('" + \
                                Archivos[Count].NewName + os.path.splitext(filename)[1] + "', '" + \
                               WORKINGPATH + Archivos[Count].Date.Year + "/" + Archivos[Count].Date.Month + "/','" + \
                                FileType + "','','','','','Ok','" + md5(dirname + '/' + filename) +  "')"
                           #print (Query)
                           DBCursor.execute(Query)
                           
                        except:
                           print ('failed copy of ' + dirname + '/' + filename )
                           Query =  "INSERT INTO Migration (Name, OldName, Path, OldPath, Type, Taken, Created, Brand, Model, Result, MD5) \
                                VALUES('" + \
                                Archivos[Count].NewName + os.path.splitext(filename)[1] + "', '" + \
                                filename + "','" + \
                                WORKINGPATH + Archivos[Count].Date.Year + "/" + Archivos[Count].Date.Month + "/','" + \
                                dirname + "','" + \
                                FileType + "','','','','','Fail','')"
                           #print (Query )
                           DBCursor.execute(Query)
            else:
                print ('File ' + filename + ' already exist')
        DBConnection.commit()                   
    print('Finish') 

    

