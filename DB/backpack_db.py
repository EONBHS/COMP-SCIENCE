import sqlite3

backpack = list()

DATABASE_FILE = "Backpack.db"

def show_backpack():
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    sql = "SELECT * FROM contents"
    cursor.execute(sql)
    results = cursor.fetchall()
    print(f"{'Index':<8}{'Name':<20}{'Description':<60}")
    for item in results:
        print(f"{item[0]:<8}{item[1]:<20}{item[2]:<60}")
    connection.close()

def get_item():
    item = input("Name?")
    description = input("Description?")
    add_item(item,description)


def add_item(item_name, item_description):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    sql = "INSERT INTO contents(name,description) VALUES (?,?)"
    cursor.execute(sql,(item_name, item_description))
    connection.commit()
    connection.close()

def delete_item(item_index):
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    sql = "DELETE FROM contents WHERE id=?;"
    cursor.execute(sql,(item_index,))
    connection.commit()
    connection.close()


   
while True:
    user_input = input("\nWhat do you want to do?\n1. Print Backpack contents\n2 Add item \n3 Delete an item \n4 Exit\n")
    if user_input == "1":
        show_backpack()
    elif user_input == "2":
        get_item()
    elif user_input == "3":
        show_backpack()
        item = int(input("\nWhat item Index do you want to delete?\n"))
        delete_item(item)
    elif user_input == "4":
        print ("\n\nGoodbye!\n\n")
        break
