import base64


def file_2_b64(path: str, name: str):
    f = open(path, 'rb')
    b64_str = base64.b64encode(f.read())
    f.close()

    utf_str = 'img = "%s"' % b64_str.decode('utf-8')
    f = open('%s.py' % name, 'w')
    f.write(utf_str)
    f.close()


if __name__ == '__main__':
    file_2_b64('C:/Users/nyanm/Downloads/aka_name_db-Database.csv', 'update_db_data')
