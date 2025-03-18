import sqlite3
import os

def check_tables():
    db = sqlite3.connect("Users.db")
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                            tg_id STRING,
                            rights STRING,
                            state STRING
                            )""")
    db.commit()
    db.close()
    db = sqlite3.connect("Storage.db")
    db.commit()
    db.close()


def get_user_info(tg_id):
    db = sqlite3.connect("Users.db")
    cursor = db.cursor()
    cursor.execute(f"""SELECT * FROM users WHERE tg_id = '{tg_id}'""")
    data = cursor.fetchone()
    db.close()
    if data is None:
        return "none", "none", "none"
    else:
        return data


async def set_state(tg_id, state):
    db = sqlite3.connect("Users.db")
    cursor = db.cursor()

    cursor.execute(f"""SELECT * FROM users WHERE tg_id = '{tg_id}'""")
    data = cursor.fetchone()
    if data is None:
        cursor.execute(f"""INSERT INTO users (tg_id, rights, state) VALUES ('{tg_id}', 'forbidden', '{state}')""")
    else:
        cursor.execute(f"""UPDATE users SET state = '{state}' WHERE tg_id = '{tg_id}'""")
    db.commit()
    db.close()

async def change_rights(tg_id, aces_level):
    db = sqlite3.connect("Users.db")
    cursor = db.cursor()
    cursor.execute(f"""UPDATE users SET rights = '{aces_level}' WHERE tg_id = '{tg_id}'""")
    db.commit()
    db.close()


def add_component(ceil, name, quantity):
    db = sqlite3.connect("Storage.db")
    cursor = db.cursor()

    cursor.execute(f"""CREATE TABLE IF NOT EXISTS Ceil_{ceil}(
                                name STRING,
                                quantity INTEGER,
                                ID STRING
                                )""")
    cursor.execute(f"""SELECT ID FROM Ceil_{ceil}""")
    data = cursor.fetchall()
    IDs = [0]
    print(data)
    if data is None:
        IDs.append(0)
    else:
        for item in data:
            item_id, = item
            IDs.append(int(item_id.split("_")[1]))
    cur_id = max(IDs) + 1
    cursor.execute(f"""INSERT INTO Ceil_{ceil} (name, quantity, ID) VALUES ('{name}', {quantity}, '{ceil}_{cur_id}')""")
    db.commit()
    cursor.execute(f"""SELECT * FROM Ceil_{ceil} WHERE ID = '{ceil}_{cur_id}'""")
    data2 = cursor.fetchone()
    db.close()
    if data2 is None:
        return False
    else:
        return True


def get_all_components(key, tg_id):
    db = sqlite3.connect("Storage.db")
    cursor = db.cursor()

    search = sqlite3.connect("SearchRes.db")
    cur_s = search.cursor()

    cursor.execute(f"""SELECT name FROM sqlite_master WHERE type='table'""")
    data = cursor.fetchall()
    items = {}
    counter = 1

    cur_s.execute(f"""DROP TABLE IF EXISTS search_{tg_id}""")
    cur_s.execute(f"""CREATE TABLE IF NOT EXISTS search_{tg_id}(
                                    num INTEGER,
                                    global_id STRING,
                                    quantity INTEGER,
                                    name STRING
                                    )""")

    for table in data:
        t_name, = table
        cursor.execute(f"""SELECT * FROM {t_name}""")
        for item in cursor.fetchall():
            name, quantity, ID = item
            if key.lower() in name.lower():
                items[counter] = (quantity, name)
                cur_s.execute(
                    f"""INSERT INTO search_{tg_id} (num, global_id, quantity, name) 
                    VALUES ({counter}, '{ID}', {quantity}, '{name}')""")
                search.commit()
                counter+=1
    db.commit()
    db.close()
    search.commit()
    search.close()
    return items


def get_item (num, tg_id):
    db = sqlite3.connect("SearchRes.db")
    cursor = db.cursor()

    cursor.execute(f"""SELECT * FROM search_{tg_id} WHERE num={num}""")
    data = cursor.fetchone()
    if data is None:
        return "None"
    else:
        return data


def update_quantity(component, delta, tg_id):
    db = sqlite3.connect("Storage.db")
    cursor = db.cursor()

    search = sqlite3.connect("SearchRes.db")
    cur_s = search.cursor()
    cur_s.execute(f"""DROP TABLE IF EXISTS search_{tg_id}""")

    cursor.execute(f"""SELECT quantity FROM Ceil_{component.split('_')[0]} WHERE ID='{component}'""")
    quantity, = cursor.fetchone()

    search.commit()
    search.close()

    if quantity:
        if quantity - delta > 0:
            cursor.execute(f"""UPDATE Ceil_{component.split('_')[0]} SET quantity = {quantity - delta} WHERE ID = '{component}'""")
        else:
            cursor.execute(f"""DELETE FROM Ceil_{component.split('_')[0]} WHERE ID = '{component}'""")
        db.commit()
        db.close()
        return True
    return False


def clear_search(tg_id):
    search = sqlite3.connect("SearchRes.db")
    cur_s = search.cursor()
    cur_s.execute(f"""DROP TABLE IF EXISTS search_{tg_id}""")
    search.commit()
    search.close()

