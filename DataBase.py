import psycopg2 as db

class DataBase:
    def __init__(self):
        self.conection = db.connect(
            host='ec2-54-166-167-192.compute-1.amazonaws.com',
            user='ormqrcwaidbsqt',
            password='74d850ecc55b4047d6fe71d85a4010babdc1b071639e0b1b027e808198d4cfdc',
            database='d41omc2js8arh3',
            port=5432)

        self.cursor = self.conection.cursor()

    def showTables(self):
        try:
            self.cursor.execute('SHOW TABLES')
            tables = self.cursor.fetchone()
            print(tables)
        except Exception as e:
            print(e)

    def createTable(self,name,colums):
        try:
            self.cursor.execute('CREATE TABLE ' + name + '( ' + colums + ' )')
        except Exception as e:
            print(e)

    def deleteTable(self,name):
        try:
            self.cursor.execute('DROP TABLE ' + name)
        except Exception as e:
            print(e)

    def insert(self,table_name,colums,values):
        try:
            self.cursor.execute('INSERT INTO ' + table_name + ' (' + colums + ') VALUES(' + values + ')')
            self.conection.commit()
        except Exception as e:
            print(e)

    def select(self,table_name):
        try:
            self.cursor.execute('SELECT * FROM ' + table_name)
            return list(self.cursor.fetchall())
        except Exception as e:
            print(e)

    def deleteAll(self,table_name):
        try:
            self.cursor.execute('DELETE FROM ' + table_name)
        except Exception as e:
            print(e)

    def close(self):
        self.conection.close()

    def getConection(self):
        return self.conection

DATABASE = DataBase()
