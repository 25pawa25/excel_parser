import sqlite3
import string

import openpyxl
from collections import defaultdict


with sqlite3.connect('data.db') as db:
    cursor = db.cursor()
    table_1 = """ CREATE TABLE IF NOT EXISTS goods(
                id_tovar INTEGER UNIQUE, 
                name_tovar TEXT, 
                barcod TEXT, 
                id_country INTEGER, 
                id_isg INTEGER
                ) """
    table_2 = """ CREATE TABLE IF NOT EXISTS country(
                id INTEGER UNIQUE, 
                name TEXT UNIQUE
                )"""
    table_3 = """ CREATE TABLE IF NOT EXISTS isg(
                id INTEGER UNIQUE,
                name TEXT
                 ) """
    cursor.execute(table_1)
    cursor.execute(table_2)
    cursor.execute(table_3)
    db.commit()



class BaseClass:

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.save_db()

    def save_db(self):
        pass


class Goods:
    count_of_country = defaultdict(int)

    def __init__(self, id, name, barcod, id_country, id_isg):
        self.id = id
        self.name = name
        self.barcod = barcod
        self.id_country = id_country
        self.id_isg = id_isg
        Goods.cnt(id_country)
        self.save_db()

    @classmethod
    def cnt(cls, id_country):
        with sqlite3.connect('data.db') as db:
            cursor = db.cursor()
            query = f"""SELECT name FROM country WHERE id = {id_country}"""
            cursor.execute(query)
            result = cursor.fetchone()
        cls.count_of_country[result] += 1
        return cls

    def save_db(self):
        with sqlite3.connect('data.db') as db:
            cursor = db.cursor()
            if self.barcod:
                query = f""" INSERT INTO goods (id_tovar, name_tovar, barcod, id_country, id_isg) VALUES({self.id}, '{self.name}', '{self.barcod}', {self.id_country}, {self.id_isg}) """
            else:
                query = f""" INSERT INTO goods (id_tovar, name_tovar, id_country, id_isg) VALUES({self.id}, '{self.name}', {self.id_country}, {self.id_isg}) """
            cursor.execute(query)
            db.commit()


class Country(BaseClass):
    count = 0

    def __init__(self, name):
        self.name = name
        Country.add_count()
        self.id = Country.count
        self.save_db()

    @classmethod
    def add_count(cls):
        cls.count += 1
        return cls

    def save_db(self):
        with sqlite3.connect('data.db') as db:
            cursor = db.cursor()
            query = f"""INSERT INTO country 
                        SELECT {self.id}, '{self.name}'
                        WHERE NOT EXISTS (SELECT 1 FROM isg WHERE name = '{self.name}')"""
            cursor.execute(query)
            db.commit()


class Isg(BaseClass):

    def save_db(self):
        with sqlite3.connect('data.db') as db:
            cursor = db.cursor()
            query = f"""INSERT INTO isg 
            SELECT {self.id}, '{self.name}' 
            WHERE NOT EXISTS (SELECT 1 FROM isg WHERE id = {self.id})"""
            cursor.execute(query)
            db.commit()


data = openpyxl.open("data.xlsx", read_only=True)
sheet = data.active


def check_country(name):
    with sqlite3.connect('data.db') as db:
        cursor = db.cursor()
        query = f"""SELECT id, name FROM country WHERE name = '{name}'"""
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            id, name = result
            return id
        else:
            return None


def check_isg(id_isg):
    with sqlite3.connect('data.db') as db:
        cursor = db.cursor()
        query = f"""SELECT id, name FROM isg WHERE id = {id_isg}"""
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            id, name = result
            return id
        else:
            return None


def check_tovar(id):
    with sqlite3.connect('data.db') as db:
        cursor = db.cursor()
        query = f"""SELECT id_tovar, name_tovar FROM goods WHERE id_tovar = {id}"""
        cursor.execute(query)
        result = cursor.fetchone()
        if result:
            id, name = result
            return id
        else:
            return None

def format_id(input_string):
    digits = string.digits
    translator = str.maketrans('', '', string.punctuation)
    result = input_string.translate(translator)
    return int(result)


for row in range(2, 1000): #sheet.max_row + 1
    id_tovar = format_id(str(sheet[row][0].value))
    tovar = sheet[row][1].value
    id_isg = sheet[row][2].value
    isg = sheet[row][3].value
    country = sheet[row][4].value
    barcod = sheet[row][5].value
    country_id = check_country(country)
    if not country_id:
        country_obj = Country(country)
        country_id = country_obj.id
    isg_id = check_isg(id_isg)
    if not isg_id:
        isg_obj = Isg(id_isg, isg)
        isg_id = isg_obj.id
    tovar_id = check_tovar(id_tovar)
    if not tovar_id:
        goods_obj = Goods(id_tovar, tovar, barcod, country_id, isg_id)
    else:
        Goods.cnt(country_id)

with open('data.tsv', 'w') as f:
    for k, v in Goods.count_of_country.items():
        f.write(f'{k[0]} - {v}\n')

data.close()







