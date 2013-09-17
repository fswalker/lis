CREATE sequence OpisProblemu_ID_seq start WITH 1 increment BY 1 no maxvalue no minvalue cache 1;
create table OpisProblemu(
        ID integer DEFAULT NEXTVAL('OpisProblemu_ID_seq') PRIMARY KEY,
        CSV text not null
);

CREATE sequence DaneBazowe_ID_seq start WITH 1 increment BY 1 no maxvalue no minvalue cache 1;
create table DaneBazowe(
        ID integer DEFAULT NEXTVAL('DaneBazowe_ID_seq') PRIMARY KEY,
        IDOpisProblemu integer references OpisProblemu (ID),
        Miasto varchar(200) not null,
        Ulica varchar(200) not null,
        X double precision not null,
        Y double precision not null,
        Z double precision not null
);

create table DaneGeograficzne(
	ID integer references DaneBazowe (ID)
);

--
-- Belgian lambert coordinate system, srid: 931370
-- insert to tabeli wewnetrznej postgisa
--
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 931370, 'epsg', 31370, '+proj=lcc +lat_1=51.16666723333333 +lat_2=49.8333339 +lat_0=90 +lon_0=4.367486666666666 +x_0=150000.013 +y_0=5400088.438 +ellps=intl +towgs84=106.869,-52.2978,103.724,-0.33657,0.456955,-1.84218,1 +units=m +no_defs ', 'PROJCS["Belge 1972 / Belgian Lambert 72",GEOGCS["Belge 1972",DATUM["Reseau_National_Belge_1972",SPHEROID["International 1924",6378388,297,AUTHORITY["EPSG","7022"]],TOWGS84[106.869,-52.2978,103.724,-0.33657,0.456955,-1.84218,1],AUTHORITY["EPSG","6313"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4313"]],UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Lambert_Conformal_Conic_2SP"],PARAMETER["standard_parallel_1",51.16666723333333],PARAMETER["standard_parallel_2",49.8333339],PARAMETER["latitude_of_origin",90],PARAMETER["central_meridian",4.367486666666666],PARAMETER["false_easting",150000.013],
PARAMETER["false_northing",5400088.438],AUTHORITY["EPSG","31370"],AXIS["X",EAST],AXIS["Y",NORTH]]');

-- geometria 3-wymiarowa
-- nazwa tabeli MUSI byc malymi literami, inaczej postgis odmawia wspolpracy
select AddGeometryColumn('danegeograficzne', 'punkt2d', 931370, 'POINT', 2);
select AddGeometryColumn('danegeograficzne', 'punkt3d', 931370, 'POINT', 3);

CREATE sequence Parametry_ID_seq start WITH 1 increment BY 1 no maxvalue no minvalue cache 1;
create table Parametry(
    ID integer DEFAULT NEXTVAL('Parametry_ID_seq') PRIMARY KEY,
    Nazwa text not null
);

create table DaneBazowe_Parametry(
    IDPunktu integer not null references DaneBazowe (ID),
    IDParametru integer not null references Parametry (ID),
    primary key (IDPunktu, IDParametru),
    Wartosc text
);

CREATE sequence GrupyWynikowe_ID_seq start WITH 1 increment BY 1 no maxvalue no minvalue cache 1;
CREATE TABLE GrupyWynikowe(
        ID integer DEFAULT NEXTVAL('GrupyWynikowe_ID_seq') PRIMARY KEY
);

CREATE sequence PasyTymczasowe_ID_seq start WITH 1 increment BY 1 no maxvalue no minvalue cache 1;
CREATE TABLE PasyTymczasowe(
        ID integer DEFAULT NEXTVAL('PasyTymczasowe_ID_seq') PRIMARY KEY,
        IDPunktu integer not null references DaneBazowe (ID), --punkt startowy dla danego pasa
        Kat double precision not null,
        Dlugosc double precision not null
);

CREATE TABLE Grupy_Punkty(
        IDGrupy integer not null references GrupyWynikowe (ID),
        IDPunktu integer not null references DaneBazowe (ID),
        Kolejnosc integer not null,
        primary key (IDGrupy, IDPunktu)
);

create table Pasy_Punkty(
        IDPasa integer NOT NULL REFERENCES PasyTymczasowe (ID),
        IDPunktu integer NOT NULL REFERENCES DaneBazowe (ID),
        primary key (IDPasa, IDPunktu)
);
