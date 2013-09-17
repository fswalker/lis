import psycopg2 as pg
from flask import g
from lanternscsv import parse_csv_string
from stripe import Stripe

# srid for Belgian Lambert coordinate system
SRID = 931370

# srid for openlayers presentation
OL_SRID = 900913

def open_connection():
    g.db = pg.connect('dbname=lanterns user=lanterns password=lanternspassword')

def close_connection():
    g.db.close()

def create_problem(csv_contents):
    unified_contents = csv_contents.replace('\r\n', '\n').replace('\r', '\n')
    curr = g.db.cursor()
    curr.execute(
        'insert into OpisProblemu (csv) values (%s) returning ID;',
        [unified_contents]);
    problemid = curr.fetchone()[0]
    data = parse_csv_string(unified_contents)

    import_data(problemid, data, curr)

    g.db.commit()
    curr.close()
    return problemid;

def delete_problem(problemid):
    curr = g.db.cursor()
    curr.execute(
        '''
            delete from Pasy_Punkty;
            delete from Grupy_Punkty;
            delete from PasyTymczasowe;
            delete from GrupyWynikowe;

            delete from DaneGeograficzne where ID in (
                select ID from DaneBazowe where IDOpisProblemu=%(problemid)s
            );

            delete from DaneBazowe where IDOpisProblemu=%(problemid)s;

            delete from OpisProblemu where ID=%(problemid)s;
        ''',
        {'problemid': problemid})

    g.db.commit()
    curr.close()

def get_csv_contents(problemid):
    curr = g.db.cursor()
    curr.execute('select csv from OpisProblemu where ID=(%s);', [problemid])
    return curr.fetchone()[0]

def import_data(problemid, data, curr):
    '''
        Initial import of data to database for a given problem
        the data dictionary is expected to have all uppercase keys
        just as it was in the supplied csv file.
    '''

    for item in data:
        curr.execute(
            '''
                insert into DaneBazowe (IDOpisProblemu, Miasto, Ulica, X, Y, Z) 
                values ((%s), (%s), (%s), (%s), (%s), (%s))
                returning ID, X, Y, Z;
            ''',
            (problemid, item['MIASTO'], item['ULICA'], item['X'],
                item['Y'], item['Z']))

        # the only way to get the generated ID without additional query
        row = curr.fetchone()
        curr.execute(
            '''
                insert into DaneGeograficzne (ID, punkt2d, punkt3d)
                values (
                    %(id)s,
                    ST_SetSRID(ST_MakePoint(%(x)s, %(y)s), %(srid)s),
                    ST_SetSRID(ST_MakePoint(%(x)s, %(y)s, %(z)s), %(srid)s)
                );
            ''',
            {'id': row[0], 'x': row[1], 'y': row[2], 'z': row[3], 'srid': SRID})

    g.db.commit()
    curr.close()


def get_data(problemid):
    curr = g.db.cursor()
    curr.execute(
        '''
            select ID, Miasto, Ulica, X, Y, Z
            from DaneBazowe
            where IDOpisProblemu=%s;
        ''',
        [problemid])
    rows = curr.fetchall()
    cols = ['ID', 'Miasto', 'Ulica', 'X', 'Y', 'Z']
    data = [dict(zip(cols, row)) for row in rows]
    curr.close()
    return data

def get_all_problem_ids():
    curr = g.db.cursor()
    curr.execute('select id from OpisProblemu')
    id_tuples = curr.fetchall()
    ids = [row[0] for row in id_tuples]
    curr.close()
    return ids

def get_points_for_open_layer(problemid):
    curr = g.db.cursor()
    curr.execute(
        '''
            select
                ST_X(ST_Transform(punkt2d, 900913)) as x,
                ST_Y(ST_Transform(punkt2d, 900913)) as y
            from danegeograficzne, danebazowe 
            where danegeograficzne.id = danebazowe.id 
            and danebazowe.idopisproblemu = (%s);
        ''', [problemid])

    rows = curr.fetchall()
    curr.close()
    return rows

def to_openlayers_projection(x, y):
    curr = g.db.cursor()
    curr.execute(
            '''
            select
                ST_X(ST_Transform(ST_PointFromText('POINT(%(x)s %(y)s)', %(srid)s), %(ol_srid)s)),
                ST_Y(ST_Transform(ST_PointFromText('POINT(%(x)s %(y)s)', %(srid)s), %(ol_srid)s));
            ''', {'srid': SRID, 'ol_srid': OL_SRID, 'x': x, 'y': y})
    rows = curr.fetchall()
    curr.close()
    return (rows[0][0], rows[0][1])

def get_first_stripe(problemid):
    curr = g.db.cursor()
    curr.execute(
        '''
            select 
                ST_X(T1.punkt2d) as x1,
                ST_Y(T1.punkt2d) as y1,
                ST_X(T2.punkt2d) as x2,
                ST_Y(T2.punkt2d) as y2,
                ST_Distance(T1.punkt2d, T2.punkt2d) as dist
            from (
                select punkt2d 
                from danegeograficzne, danebazowe 
                where danebazowe.id = danegeograficzne.id 
                and idopisproblemu = %(problemid)s
            ) T1,
            (
                select punkt2d 
                from danegeograficzne, danebazowe 
                where danebazowe.id = danegeograficzne.id 
                and idopisproblemu = %(problemid)s
            ) T2;
        ''',
        {'problemid' : problemid})

    rows = curr.fetchall()

    # get the row with the most distant points
    longest = max(rows, key=lambda row: int(row[4]))
    (x1, y1) = (longest[0], longest[1])
    (x2, y2) = (longest[2], longest[3])
    length = longest[4]

    curr.close()
    return Stripe(x1, y1, x2, y2, length)

def get_points_in_stripe(problemid, stripe):
    curr = g.db.cursor()
    sql = '''
        select
            id, ST_X(punkt2d) as x, ST_Y(punkt2d) as y
        from
            (select 
                DaneGeograficzne.ID,
                punkt2d,
                ST_Buffer(ST_GeomFromText('LINESTRING(%(x1)s %(y1)s, %(x2)s %(y2)s)', %(srid)s), %(width)s) AS Pas
            from DaneGeograficzne
            join DaneBazowe on DaneGeograficzne.ID = DaneBazowe.ID
            where IDOpisProblemu = %(problemid)s) AS Temp
        where ST_Within(punkt2d, Pas);
    '''

    curr.execute(sql,
        {'problemid': problemid,
        'x1': stripe.x1,
        'y1': stripe.y1,
        'x2': stripe.x2,
        'y2': stripe.y2,
        'srid': SRID,
        'width': stripe.width}
    );

    rows = curr.fetchall()
    curr.close()
    return [{'id': row[0], 'x': row[1], 'y': row[2]} for row in rows]

def rotate_stripe(stripe, radians):
    curr = g.db.cursor()
    sql = '''
        select
            ST_X(ST_StartPoint(Obr)) as x1, ST_Y(ST_StartPoint(Obr)) as y1,
            ST_X(ST_EndPoint(Obr)) as x2, ST_Y(ST_EndPoint(Obr)) as y2
        from
            (select
                ST_Rotate(Linia, %(rad)s, ST_Centroid(Linia)) as Obr
                from 
                    (select
                        ST_GeomFromText(
                            'LINESTRING(%(x1)s %(y1)s, %(x2)s %(y2)s)',
                            %(srid)s) AS Linia
                    ) as Temp1
            ) as Temp2;
        '''
    curr.execute(sql, {
        'x1': stripe.x1,
        'y1': stripe.y1,
        'x2': stripe.x2,
        'y2': stripe.y2,
        'srid': SRID,
        'rad': radians})

    row =  curr.fetchall()[0]
    curr.close()
    return Stripe(row[0], row[1], row[2], row[3], stripe.length, stripe.width)

def add_stripe_to_db(pointDicts):
    if len(pointDicts) == 0:
        return

    curr = g.db.cursor()
    # random values - not needed
    sql = '''
        insert into PasyTymczasowe (IDPunktu, Kat, Dlugosc) 
            values (%(pointId)s, 0.0, 0.0) returning ID;
        '''
    # random value - not needed
    curr.execute(sql, {'pointId': pointDicts[0]['id']})
    stripeId = curr.fetchall()[0]
    for pointDict in pointDicts:
        sql = '''
            insert into Pasy_Punkty (IDPasa, IDPunktu)
            values (%(stripeId)s, %(pointId)s);'''
        curr.execute(sql, {'stripeId': stripeId, 'pointId': pointDict['id']})

def delete_all_stripes_and_groups():
    curr = g.db.cursor()
    curr.execute('''
        delete from Pasy_Punkty;
        delete from PasyTymczasowe;
        delete from Grupy_Punkty;
        delete from GrupyWynikowe;''')
    g.db.commit()
    curr.close()

def add_group_to_db(pointDicts):
    if len(pointDicts) == 0:
        return

    curr = g.db.cursor()
    curr.execute('''insert into GrupyWynikowe default values returning ID;''')
    groupId = curr.fetchall()[0]

    order = 1
    for pointDict in pointDicts:
        sql = '''
            insert into Grupy_Punkty (IDGrupy, IDPunktu, Kolejnosc)
            values (%(groupId)s, %(pointId)s, %(order)s);'''
        curr.execute(sql,
            {'groupId': groupId,
            'pointId': pointDict['id'],
            'order': order})
        order += 1
    g.db.commit()
    curr.close()

def get_group_ids():
    curr = g.db.cursor()
    curr.execute('select id from GrupyWynikowe;')
    rows = curr.fetchall()
    curr.close()
    return [row[0] for row in rows]

def get_points_in_group(groupid):
    curr = g.db.cursor()
    curr.execute('''
        select ST_X(punkt2d), ST_Y(punkt2d)
        from GrupyWynikowe, Grupy_Punkty, DaneGeograficzne
        where Grupy_Punkty.IDGrupy = GrupyWynikowe.ID
        and Grupy_Punkty.IDPunktu = DaneGeograficzne.ID
        and GrupyWynikowe.ID = %(groupid)s''',
        {'groupid': groupid})
    rows = curr.fetchall()
    curr.close()
    return rows