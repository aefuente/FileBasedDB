import sys
import random
import os.path
import os
import csv
import ast

def is_file(file_name):
    """
    Checks if file exists
    """
    if not os.path.isfile(file_name):
        print('')
        print(file_name, "not found")
    return os.path.isfile(file_name)



def new_file_tag(file_name, tag='.forgot'):
    """
    A quick way to create new file names
    """
    if tag == '.forgot':
        print("Forgot file tag")
    prop = file_name.find('.')
    return file_name[:prop] + tag






def set_seek(f, location, record_size):
    """
    Sets the seek position to a location in the records
    """
    f.seek(0,0)
    f.seek(location * (record_size+1))


def sep_line_data(line, fields):
    """
    Reads data from fixed length data file
    """

    # Seperate the fields
    field_array = line.split()
    field = list(fields.keys())

    # Creating the record dictionary
    record = {}
    for i in range(len(field)):
        record[field[i]] = field_array[i].replace('_',' ')

    # Return the record dictionary
    return record


def write_data(f,record,fields_size):
    """
    Writes record to file
    """
    line = ''
    
    for key in record.keys():
        line = (line + record[key].replace(' ','_').ljust(fields_size[key], ' '))
    print(line.strip('\n'), file=f)





class Database_MG():
    """
    Class for managing the databases
    """


    def __init__(self):
        # Is true if a database is open
        self.open = False
        # Holds the current open data base
        self.file_name = ''
        # Holds the fields and number of records from config file
        self.fields = []
        self.num_records = 0
        self.num_record_slots = 0
        self.record_size = 0



    def create_report(self):
        '''
        Write a report to the console as well as to a file
        '''
        # Sets the seek of the database to the beginning
        self.f.seek(0,0)
        # Keeps track of how many records have been written to the report
        submitted = 0
        # Opens the new report file
        # Read the first line
        record = self.f.readline()

        with open(new_file_tag(self.file_name,'_report.txt'), 'w') as report:
            while(submitted < 10 and record is not ''):
                # If the record is not blank write it to the report
                if(record[0] is not ' '):
                    # Creates the record dictionary
                    record = sep_line_data(record,self.fields)
                    
                    # Increase the report number
                    submitted+=1

                    # Write to report
                    print('\n\n' + '*' * 70)
                    print('\n\n' + '*' * 70, file=report)
                    print("Report item #{}".format(submitted))
                    print("Report item #{}".format(submitted), file=report)
                    print('\n')
                    print('\n',file=report)
                    for item in record.keys():
                        print("{: <20}:\t {: <20}".format(item,record[item]))
                        print("{: <20}:\t {: <20}".format(item,record[item]), file=report)
                    print('\n\n'+ '*' * 70 + '\n\n')
                    print('\n\n'+ '*' * 70 + '\n\n', file=report)
                
                # Reads in the fixed length record
                record = self.f.readline()



    def truncate_data(self,key,value):
        '''
        Make the field less than the max field size
        '''
        if (self.fields[key] <= len(value)):
            value = value[:self.fields[key]-1]
        return value



    def order_db(self, record_size, record, previous, first=False):
        """
        Method for re-organizing the database. It creates a temp
        file that over-writes our data file.
        """
        # Keeps track of how many lines are in the database
        total_lines = 0
        
        # Sets the file pointer to the beginning of file
        self.f.seek(0,0)

        # Keeps track if the data was recorded
        recorded = False

        # Gets the first line
        line = self.f.readline()

        # Creating an updated tmp file that overwrites our outdated data file
        with open('tmp.file', 'w') as w:

            # Special case where the new record needs to be the first
            if first:
                # Write the record
                write_data(w,record,self.fields)
                print(' ' * (self.record_size),file=w)
                total_lines += 2
                recorded = True

            # Loops through the entire file
            while(line != ''):

                # Else write a non-blank line
                if(line is not '' and line[0] != ' '):
                    print(line.strip('\n').ljust(self.record_size, ' '),file=w)
                    print(' ' * (self.record_size),file=w)
                    total_lines += 2

                    if (previous ==line):
                        write_data(w,record,self.fields)
                        print(' ' * (self.record_size),file=w)
                        total_lines +=2
                        recorded = True

                # Get the next line
                line = self.f.readline()
            # The case where we need to add an extra line to the bottom of the file
            if not recorded:
                write_data(w,record,self.fields)
                print(' ' * (self.record_size),file=w)
                total_lines += 2
        
        # Close the file
        self.f.close()
        # Replace the data file with the new tmp file
        os.replace('tmp.file',self.file_name)
        # Open the updated data file
        self.f = open(self.file_name, 'r+')


        # Return the total number of lines in the database
        return total_lines
           


    def add_record(self,record):
        """
        Add a record to the DB
        """

        # Key for the ID
        key = next(iter(record))

        # Gets the location of where the item should be inserted
        found, location = self.binary_search(int(record[key]))

        # When found is -1 this means they are trying to duplicated a record
        if found is not -1:
            print("You cannot use the same id for two records")
            return

        # Truncates the data if too large
        for item in record.keys():
            record[item] = self.truncate_data(item,record[item])

        # Sets the file pointer to the location returned by binary  search
        set_seek(self.f, location,self.record_size)
        # Gets the line
        line = self.f.readline()

        # If we landed on a filled space check if we need to insert
        # before or after and keep the insert location updated
        if(line != '' and line[0] is not ' '):

            # If the record is large than the current line move to the next line
            if int(line[:line.find(' ')]) < int(record[key]):

                # Get the next line
                tmp = line 
                line= self.f.readline()

                # If the record is smaller than the next line move back to previous line
                # (This is so when we write the database we can just write immediately under previous)
                try:
                    if(line != '' and int(record[key]) < int(line[:line.find(' ')])):
                        line = tmp
                        location -=1
                except ValueError:
                    pass
                location += 1

            #If the record is smaller than the current line go to the line above it
            else:
                if location-1 > 0:
                    set_seek(self.f,location-1,self.record_size)
                else:
                    set_seek(self.f,0,self.record_size)
                line = self.f.readline()
                location -=1

        # Now we check the new location, if there is an empty spot, great we can insert
        if (line is not '' and line[0] is ' '):
            set_seek(self.f,location,self.record_size)
            write_data(self.f,record,self.fields)
            self.num_records +=1
        
        # If the new location is already full, we have to re-write the DB
        else:
            # My re-write works by just writing the new line after line we just calculated
            if(location >= 0):
                self.num_record_slots = self.order_db(self.record_size,record,line)
                self.num_records = self.num_record_slots  //2
        
            # The case where it is the first item and there is no "previous line"
            else:
                self.num_record_slots = self.order_db(self.record_size,record,'isfirst',first=True)
                self.num_records = self.num_record_slots  //2
    


    def delete_record(self,record_id):
        """
        Deletes a record_id from the database
        """
        
        # Searches the database for the record_id
        found, location = self.binary_search(record_id)
        
        # Print a message when the record is not found
        if found is -1:
            return False, -1


        # Over-write the record that is to be deleted
        set_seek(self.f,location,self.record_size)
        print(' ' * (self.record_size),file=self.f)
        self.num_records -= 1 
        # Return true and the record
        return True, found    



    def update_record(self, name):
        """
        Updates one field of a singular record
        """

        # Find the location of the record
        record, location = self.binary_search(name)
        
        # If the record is found print it out.
        if record is not -1:
            print('\n\n' + '*' * 70)
            print('\t\t\tRecord:', name, end='\n\n')
            for item in record.keys():
                print("{: <20}:\t {: <20}".format(item,record[item]))
            print('\n\n'+ '*' * 70 + '\n\n')

        # IF the record is not found show the user
        else:
            print('\n\n' + '*' * 70)
            print('\n\nRecord was not found')
            print('\n\n' + '*' * 70)
            return

        # Get the field the user wants to change
        no_change = next(iter(record))
        key = no_change
        while(key == no_change):
            key = input('Type the field you wish to change (you cannot change the primary key): ')
            for item in record.keys():
                if (key == item):
                    break
            else:
                key = no_change

        # Get the value of the field from the user
        value = input('Enter the value: ')
        while(len(value) == 0):
            value = input('Enter the value: ')

        #Cut the data if its to big
        value = self.truncate_data(key,value)

        # Assign the fields new value
        record[key] = value        

        # Point to the location to print
        set_seek(self.f,location,self.record_size)
        
        # Write to the DB
        write_data(self.f,record,self.fields)

        # Print the updated record
        print('\n\n' + '*' * 70)
        print('\t\tUpdated Record:', name, end='\n\n')
        for item in record.keys():
            print("{: <20}:\t {: <20}".format(item,record[item]))
        print('\n\n'+ '*' * 70 + '\n\n')


    
    
    def get_record(self, num_record, record_size):
        """
        Scans file for location produced by the binary search
        """

        record = "not found"
        # If we land on a blank move onto the next one and track shifts
        shift = 0
        
        # Get the record at the location produced by BS
        if num_record >= 0 and num_record < self.num_record_slots:

            # Set file pointer to head
            set_seek(self.f,num_record,record_size)

            # Read the record
            record = self.f.readline()
        
        # If we don't find a record at this location continue searching the file
        while(record is not '' and record[0] == ' '):
            record = self.f.readline()
            shift +=1

        # Return the record and the number it may have been shifted by
        return record, shift



    def binary_search(self,name):
        """
        Binary search to scan for primary key
        """
        
        # Holds true of the  record is found
        found = False
        high = self.num_record_slots-1
        low = 0

        while not found and high >= low:
            middle = (low+high) // 2
            record, shift = self.get_record(middle, self.record_size)
            if(record is ''):
                return -1, middle
            middle_id = int(record.split(' ')[0])
            if middle_id == name:
                found = True
            if middle_id < name:
                low = middle+1
            if middle_id > name:
                high = middle-1

        # If found returned the parsed data and it's location
        if (found == True):
            return sep_line_data(record,self.fields), middle+ shift
        else:
            return -1, middle



    def create_new_config(self, file_name, fields, record_size, num_records, num_record_slots):
        """
        My configs will be sotred as dictionaries for easy
        retrieval
        """
        
        #Check if the file exists.
        is_file(file_name)
        # Store the count into a dictionary
        # Create config file name
        config_file = new_file_tag(file_name, tag='.config')
        with open(config_file, 'w') as w:
            print(fields, file=w)
            print("{{'record_size': {}}}".format(record_size),file=w)
            print("{{'num_records': {}}}".format(num_records), file=w)
            print("{{'num_record_slots': {}}}".format(num_record_slots), file=w)



    def create_new_db(self,file_name):
        """
        Create the database files
        """
        
        # Check if the file is there
        if(not is_file(file_name)):
            return False

        # Create the new data file tag
        data_file = new_file_tag(file_name, tag='.data')
        
        # If parks.data already exists give the user an option to overwrite it
        if is_file(data_file):
            print()
            overwrite = ''
            while (overwrite is not 'y' and overwrite is not 'n'):
                overwrite = input('{} is already a database, would you like overwrite it?(y/n): '.format(data_file[:data_file.find('.')]))
            if overwrite == 'n':
                return False
            if overwrite == 'y' and self.open and file_name == self.file_name:
                print("\nClosing {} so {} can be re-written\n".format(data_file[:data_file.find('.')],data_file[:data_file.find('.')])) 
                self.close_db()
                
        num_records = 0
        record_size = 0

        # Open the file
        with open(file_name, 'r') as f:

            # Seperate the fields into a list
            fields = f.readline().strip().split(',')
            field_size = {}
            for item in fields:
                field_size[item] = 0
            reader = csv.DictReader(f)

            f.seek(0,0)
            # Count the side of each field
            for record in reader:
                for key in record.keys():
                    if(len(record[key])+1 >= field_size[key]):
                        field_size[key] = len(record[key])+1

                # The size of DB we will need
                num_records += 2


            # Get field size
            for key in field_size.keys():
                record_size += field_size[key]

            f.seek(0,0)
            # Write the data file
            with open(data_file, 'w') as w:
                
                # Create csv reader object
                reader = csv.DictReader(f)
                line = ''

                # conver file into fixed length records
                for record in reader:
                    for key in record.keys():
                        line = (line + record[key].replace(' ','_').ljust(field_size[key], ' '))
                    print(line.strip('\n'), file=w)
                    line = ''
                    print(' ' * record_size, file=w)

        # When creating a database we create the config
        self.create_new_config(file_name,field_size,record_size,num_records//2,num_records)
        return True



    def set_metadata(self):
        """
        Opens the config file and reads upon opening a new database
        """
        # Set the config file name
        config_file = new_file_tag(self.file_name, tag='.config')

        # Gets the field lengths and number of records
        with open(config_file, 'r') as r:
            self.fields = ast.literal_eval(r.readline())
            self.record_size = int(ast.literal_eval(r.readline())['record_size'])
            self.num_records = int(ast.literal_eval(r.readline())['num_records'])
            self.num_record_slots = int(ast.literal_eval(r.readline())['num_record_slots'])



    def open_db(self):
        """
        Open a database. Sets the file read object.
        """

        # If database is already open fail and tell the user
        if self.open:
            print("Please close the opened database before opening a new one\n")
            return

        # Attempt to open a database
        name = input('Please enter the prefix of your database: ')
        data_file = name + '.data'
        config_file = name + '.config'

        # If file is not found fail and tell the user
        if not is_file(data_file) or not is_file(config_file):
            print("\n\nThis database does not exist or hasn't been configured properly.")
            print("Enter in the correct name or create a new database\n")
            return
       
        print("\n\nSuccesfully opened {} database....\n".format(name))
        # Set the data file, open it, write the metadata
        self.file_name = data_file
        self.open = True
        self.set_metadata()
        self.f = open(data_file, 'r+')



    def close_db(self):
        """
        Close a database. Closes files, updates config.
        """
        self.create_new_config(self.file_name, self.fields, self.record_size, self.num_records, self.num_record_slots)
        self.file_name = ''
        self.record_size = 0
        self.num_records = 0
        self.num_record_slots = 0
        self.fields = 0
        self.open = False
        self.f.close()
