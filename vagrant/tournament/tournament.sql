-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- we first delete all the existing tables with the same name

DROP TABLE IF EXISTS players_c CASCADE;
DROP TABLE IF EXISTS tournaments CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS matches CASCADE;
DROP TABLE IF EXISTS rounds CASCADE;
DROP VIEW IF EXISTS playstats;
DROP VIEW IF EXISTS pairing;

-- We create the tournaments table to store all the informations about
-- a given tournaments.
-- Variables:
--     id_tournament(SERIAL): a unique id for the
--     name_t(TEXT): the name of the tournament
--     date_t(DATE): the date when the tournament takes place
-- Unique key:
--     the id_tournament has to be unique

CREATE TABLE tournaments ( id_tournament SERIAL,
                           t_name TEXT,
                           t_date DATE DEFAULT CURRENT_DATE,
                           PRIMARY KEY (id_tournament));


-- We create the players_c table to store information that won't change for
-- a player.
-- Variables:
--     id_player_c(SERIAL): a unique id identifying the player
--     p_sname(TEXT): the first name of the player
--     p_name(TEXT): the name of the player
-- Unique key:
--     the id_player_c has to be unique

CREATE TABLE players_c ( id_player_c SERIAL,
                         p_sname TEXT,
                         p_name TEXT,
                         PRIMARY KEY (id_player_c));


-- We create the player table to store all the characteristics of a player in
-- a given tournament.
-- Variables:
--     id_player(SERIAL): an unique id for the player
--     id_player_c(INTEGER): a foreign key used in the players_c table to link
--                           the player specific only informations
--     wins(INTEGER): the total number of victories of the player in a
--                    given tournament
--     matches(INTEGER): the total number of matches of the player in a given
--                       tournament
--     tournament(INTEGER): a tournament where a player is registered in
-- Unique key:
--     the id_player, tournament pair has to be unique

CREATE TABLE players ( id_player SERIAL,
                       id_player_c INTEGER,
                       wins INTEGER DEFAULT 0,
                       matches INTEGER DEFAULT 0,
                       tournament INTEGER REFERENCES tournaments(id_tournament),
                       FOREIGN KEY (id_player_c) REFERENCES
                                   players_c(id_player_c),
                       PRIMARY KEY (id_player, tournament));


-- We create the matches table to store all the characteristics of a matche in
-- a given tournament at a given round.
-- Variables:
--     id_match(SERIAL): an unique id for the match
--     score_p1(INTEGER): the score of the first player
--     score_p2(INTEGER): the score of the second player
--     tournament(INTEGER): a tournament where a player is registered in
--     id_p1(INTEGER): the unique id assigned to the first player/tournament
--                     pair
--     id_p2(INTEGER): the unique id assigned to the second player/tournament
--                     pair
-- Unique key:
--     the id_match, tournament, id_p1, id_p2 quartet has to be unique

CREATE TABLE matches ( id_match SERIAL,
                       -- round INTEGER,
                       score_p1 INTEGER DEFAULT 0,
                       score_p2 INTEGER DEFAULT 0,
                       tournament INTEGER,
                       id_p1 INTEGER,
                       id_p2 INTEGER,
                       FOREIGN KEY (id_p1, tournament) REFERENCES
                                   players(id_player, tournament),
                       FOREIGN KEY (id_p2, tournament) REFERENCES
                                   players(id_player, tournament),
                       PRIMARY KEY (id_match, tournament, id_p1, id_p2));


-- A view to retrieve players characteristics, names and tournaments infos

CREATE VIEW playstats AS
    SELECT id_player, p_sname, p_name, t_name, wins, matches, tournament
    FROM players, players_c, tournaments
    WHERE players.id_player_c = players_c.id_player_c
    AND tournaments.id_tournament = players.tournament
    ORDER BY wins DESC;


-- A view to add the ranking of each player

CREATE VIEW interrank AS
       SELECT id_player, p_sname, p_name, wins, matches, tournament, t_name,
       int4(row_number() over(order by wins)) as r1
       from playstats
       order by wins DESC;


-- A view to build pairs of adjacent players in terms of ranking

CREATE VIEW pairing AS
    SELECT ir1.id_player as id1, ir1.p_sname as p1_sname, ir1.p_name as p1_name,
           ir2.id_player as idp2, ir2.p_sname as p2_sname, ir2.p_name as p2_name
    FROM interrank as ir1, interrank as ir2
    WHERE ir1.tournament = ir2.tournament
    AND ir1.matches = ir2.matches
    AND ir1.r1=(ir2.r1-1)
    AND ir2.r1%2=0;
