import sys
import os.path
import csv
import dbmg


"""


Class for handling the User interface


"""



class User_Interface():
    def __init__(self):
        self.quit = False
        self.db_mg = dbmg.Database_MG()
    def is_open(self, message):
        if not self.db_mg.open:
            print('\n\n' +('-' * 70))
            print("\n\nYou must open a database before you can {}...\n\n".format(message))
            print(('-' * 70)+'\n\n')
            return False
        return True


    def get_user_int(self, field,action):
            ID = ''
            correct = False
            while(not correct):
                ID = input("Enter in the record {} you would like to {}: ".format(field,action))
                try:
                    if (int(ID)>= 0):
                        correct = True
                    else:
                        print("\n\nPlease enter positive integers only\n\n")
                except ValueError:
                    print("\n\nPlease enter integers only\n\n")

            return int(ID)


    def create_new_db(self):
        print('\n\n' +('-' * 70))
        print("\nYou have selected to create a new database...", end='\n\n\n')
        name =  input("Please enter the csv file's name: ")
        if(self.db_mg.create_new_db(name)):
            print("\n\nDatabase "+ name[:name.find('.')] + ' was succesfully created')
        else:
            print("\n\nCreating database with file \""+ name + '\" failed')
        print('\n' + '-' * 70, end='\n\n\n')

    def open_db(self):
        print('\n\n' +('-' * 70))
        print('\nYou have selected to open an existing database....', end='\n\n\n')
        self.db_mg.open_db()
        print( '-' * 70, end='\n\n\n')
    
    def close_db(self):
        if self.db_mg.open:
            print('\n\n' + ('-' * 70))
            print('\n\nClosing {} database...'.format(self.db_mg.file_name[:self.db_mg.file_name.find('.')]), end='\n') 
            print('\n\n' + ('-' * 70))
            self.db_mg.close_db()
        else:
            print('\n\n' + ('-' * 70))
            print('\n\nYou are trying to close a database when none are open', end='\n') 
            print('\n\n' + ('-' * 70) + '\n\n')

    def display_record(self):
        if self.is_open('display a record'):
            print('\nYou would like to display a record....', end='\n\n')
            name = self.get_user_int('ID','dislpay')
            record, middle = self.db_mg.binary_search(name)
            if (record != -1):
                print('\n\n'+'*' * 70)
                print('\t\t\tRecord:',name,end='\n\n')
                for item in record.keys():
                    print("{: <20}:\t {: <20}".format(item,record[item]))
                print('\n\n'+'*' * 70)
            else:
                print('\n\n'+'*' * 70)
                print('\n\nRecord {} was not found'.format(name))
                print('\n\n'+'*' * 70)

    def update_record(self):
        if self.is_open('update a record'):
            print('\nYou would like to update a record....', end='\n\n')
            ID = self.get_user_int('ID','update')
            self.db_mg.update_record(ID)

    def create_report(self):
        if self.is_open('create a report'):
            print('\nWriting the report....',end='\n\n')
            self.db_mg.create_report()

    def add_record(self):
        if self.is_open('add a record'):
            record = {}
            print('\nAdding a record....', end='\n\n')
            print('\n\n'+'*' * 70 + ('\n\n'))
            for item in self.db_mg.fields:
                if item == 'ID':
                    tmp = self.get_user_int('ID','add')
                else:
                    tmp = input("Enter the {: <10}:\t".format(item))
                record[item] = str(tmp)
            print('\n\n'+'*' * 70 + ('\n\n'))
            self.db_mg.add_record(record)
        


    def delete_record(self):
        if self.is_open("delete a record"):
            print("\n\nYou have selected to delete a record...",end="\n\n")
            ID = self.get_user_int('ID','delete')
            found, record = self.db_mg.delete_record(ID)
            if found:
                print("\n\nYou deleted the following record...") 
                print('*' * 70)
                print('\t\t\tRecord:',ID,end='\n\n')
                for item in record.keys():
                    print("{: <20}:\t {: <20}".format(item,record[item]))
                print('\n\n'+('*' * 70) + '\n\n')
            else:
                print('\n\n' +('-' * 70))
                print("\n\nThe ID given to delete was not found\n\n")
                print(('-' * 70)+ '\n\n')

    def stop(self):
        print('\n\n' +('-' * 70))
        if self.db_mg.open:
            print("\n\nYou left a database open, safely shutting down...")
            self.db_mg.close_db()
        print("\n\nExiting....\n\n")
        print(('-' * 70)+ '\n\n' )
        self.quit = True

    def run(self):
        print("\n" + ('*') * 70)
        print("*" + (' ' * 68) + '*')
        print("*" + (' ' * 68) + '*')
        print("*\t   Welcome to Andre's record management system" + (' ' * 15) + '*')
        print("*" + (' ' * 68) + '*')
        print("*" + (' ' * 68) + '*')
        print('*' * 70, end='\n\n\n')
        selection = {
                    1 : self.create_new_db,
                    2 : self.open_db,
                    3 : self.close_db,
                    4 : self.display_record,
                    5 : self.update_record,
                    6 : self.create_report,
                    7 : self.add_record,
                    8 : self.delete_record,
                    9 : self.stop,
                    }
        while not self.quit:
            if(self.db_mg.open):
                print("With {} open please enter the number next to the command you wish to use\n".format(self.db_mg.file_name[:self.db_mg.file_name.find('.')]))
            else:
                print("Please enter the number next to the command you wish to use\n")
            print("\t1) Create a new database")
            print("\t2) Open a database")
            print("\t3) Close a database")
            print("\t4) Display record")
            print("\t5) Update record")
            print("\t6) Create report")
            print("\t7) Add record")
            print("\t8) Delete record")
            print("\t9) Quit", end="\n\n")
            try:
                answer = int(input("Answer: "))
            except ValueError:
                answer = 0
            if 0 < answer and answer <= 9:
                selection[answer]()
            else:
                print('\n\n' +('-' * 70))
                print("\nPlease enter a valid integer between 1 and 9", end='\n\n')
                print(('-' * 70)+'\n\n')
        


def main():
    #file_name = input("Open a data base. What is the name of the file: ")
    #meta_data = create_meta_data(file_name)
    #print(meta_data)
    #create_data('Parks.csv')
    UI = User_Interface()
    UI.run()

main()
