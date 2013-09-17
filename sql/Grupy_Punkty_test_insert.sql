INSERT INTO OpisProblemu(ID, CSV) VALUES(1, 'id;miasto');
INSERT INTO DaneBazowe(ID, IDOpisProblemu, Miasto, Ulica, X, Y, Z) VALUES(1, 1, 'Sanok', 'Kolataja', 2.3, 3.45, 2.34),
(2, 1, 'Sanok', 'Kolataja', 2.3, 3.45, 2.34);
INSERT INTO GrupyWynikowe(ID) VALUES(1), (2), (3), (4);
INSERT INTO Grupy_Punkty(IDGrupy, IDPunktu, Kolejnosc) VALUES(1,1,1), (2,1,3), (3,1,2), (1,2,2), (4,2,1);
