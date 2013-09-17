from flask import g
import csv, os

CSV_DELIMITER = ';'
RESULT_CSV_FILE = 'lampy1.csv'
csv.register_dialect('lanternsDialect', delimiter=';', doublequote=False)

def is_correct_csv_filename(filename):
    (name, ext) = os.path.splitext(filename)
    return ext.lower() == '.csv'

def get_first_csv_line(file):
    csvreader = csv.reader(file, delimiter=CSV_DELIMITER)
    return csvreader.next()

# returns a list of dictionaries
def parse_csv_string(s):

    def force_dot_decimal_separator(data):
        for item in data:
            def comma2dot(x):
                item[x] = item[x].replace(',', '.')
            comma2dot('X')
            comma2dot('Y')
            comma2dot('Z')
        return data

    lines = [line for line in s.split('\n') if line.strip() != '']

    csvreader = csv.reader(lines, delimiter=CSV_DELIMITER)
    # first line as column names
    cols = csvreader.next()
    data = [dict(zip(cols, row)) for row in csvreader]
    return force_dot_decimal_separator(data)

def save_to_csv(contents):
    csv_file = open(RESULT_CSV_FILE, "w")
    csv_file.write(contents)
    csv_file.close()

def get_groups_and_sequences(pointid, idoffset):
    curr = g.db.cursor()
    curr.execute(
    '''
    select idgrupy, kolejnosc
    from grupy_punkty
    where idpunktu = %s;
    ''',
    [pointid + idoffset])

    rows = curr.fetchall()
    cols = ['IDGrupy', 'kolejnosc']
    data = [dict(zip(cols, row)) for row in rows]
    print data
    curr.close()
    return data
 
def get_first_point_for_current_problem():
     curr = g.db.cursor()
     curr.execute('''
        select idpunktu from grupy_punkty limit 1;     
     ''')
     pointid = curr.fetchall()[0][0]
          
     curr.execute('''
        select idopisproblemu from danebazowe where id = %s;
     ''', [pointid])
     
     problemid = curr.fetchall()[0][0]
     
     curr.execute('''
        select min(id) from danebazowe where idopisproblemu = %s;
     ''', [problemid])
     
     minpointid = curr.fetchall()[0][0]
     curr.close()          
     return minpointid   


def exportUpdatedCSVFile():
    try:
        updatedCSVContent = []
        #Open csv file
        with open(RESULT_CSV_FILE, 'r') as result_csv:
            csvDictReader = csv.DictReader(result_csv, dialect = 'lanternsDialect')

            fieldNames = csvDictReader.fieldnames
            if 'GRUPA' in fieldNames and 'KOLEJNOSC' in fieldNames:
                return True
            maxPairsAmount = 0
            #Iterate through all lanterns
            idoffset = get_first_point_for_current_problem()
            for row in csvDictReader:
                csv_line = []
                for fieldName in fieldNames:
                    csv_line.append(row[fieldName])
                #Iterate through all pairs (group, order) and add to the result line
                currentPairsAmount = 0
                for pair in get_groups_and_sequences(int(row['NR']), idoffset):
                    print pair
                    csv_line.append(str(pair['IDGrupy']) + ';' + str(pair['kolejnosc']))
                    currentPairsAmount += 1
                if currentPairsAmount > maxPairsAmount:
                    maxPairsAmount = currentPairsAmount
                updatedCSVContent.append(';'.join(csv_line))

        with open(RESULT_CSV_FILE, 'w') as updated_csv:
            for i in range(maxPairsAmount):
                fieldNames.append( 'GRUPA;KOLEJNOSC' )
            updated_csv.write(';'.join(fieldNames))
            for line in updatedCSVContent:
                updated_csv.write('\n' + line)
        return True
    except IOError:
        print 'There is no csv file!'
        return False
