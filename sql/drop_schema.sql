drop table if exists Pasy_Punkty;
drop table if exists Grupy_Punkty;
drop table if exists PasyTymczasowe;
drop table if exists GrupyWynikowe;
drop table if exists DaneBazowe_Parametry;
drop table if exists Parametry;
drop table if exists DaneGeograficzne;
drop table if exists DaneBazowe;
drop table if exists OpisProblemu;

drop sequence if exists OpisProblemu_ID_seq, DaneBazowe_ID_seq, Parametry_ID_seq, GrupyWynikowe_ID_seq,
PasyTymczasowe_ID_seq;

-- remove belgian lambert coordinate system reference
delete from spatial_ref_sys where srid=931370;
