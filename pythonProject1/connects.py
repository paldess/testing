import pymysql


def connect_write(sql):
    connection = pymysql.connect(host='176.193.70.199',
                             user='test',
                             password='12345',
                             database='test',
                             port=3313,
                             autocommit=True)
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                cursor.connection.commit()
        return True
    except:
        return False

def connect_read(sql, dict=False):
    if dict == True:
        connection = pymysql.connect(host='176.193.70.199',
                                     user='test',
                                     password='12345',
                                     database='test',
                                     port=3313,
                                 cursorclass=pymysql.cursors.DictCursor)
    else:
        connection = pymysql.connect(host='176.193.70.199',
                                     user='test',
                                     password='12345',
                                     database='test',
                                     port=3313)
    try:
        with connection.cursor() as cursor:
            # Read a single record
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    except:
        return False