from tinydb import TinyDB, Query


file_loc = "./exp.db.json"
db = TinyDB(file_loc)

Q = Query()
exps = db.search(Q.result == None)
print("DONE:", len(db)-len(exps))
print("TODO:", len(exps))

if input("View finished ones? (y/n) ") == "y":
    for exp in db.search(Q.result != None):
        print(exp)

if input("View unfinished ones? (y/n) ") == "y":
    for exp in db.search(Q.result == None):
        print(exp)
