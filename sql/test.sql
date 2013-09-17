--select st_punkt2d from danegeograficzne limit 5;
--select ST_Distance(p1, p2) as dist
--from (select
--        ST_GeographyFromWKB(select dane1.punkt2d from danegeograficzne as dane1 where dane1.id = 1) as p1,
--        ST_GeographyFromWKB(select dane2.punkt2d from danegeograficzne as dane2 where dane2.id = 2) as p2,
--    ) as foo;
select st_issimple(d.punkt2d) from danegeograficzne as d where id = 1;