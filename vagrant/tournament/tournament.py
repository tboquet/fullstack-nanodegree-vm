#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteTournaments():
    """Remove all the tournaments records from the database."""
    conn = connect()
    query = """delete from tournaments cascade;"""
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    query = """delete from matches cascade;"""
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()


def deletePlayersC():
    """Remove all the player records from the database."""
    conn = connect()
    query = """delete from players_c cascade;"""
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the registrations of all players from the database."""
    conn = connect()
    query = """delete from players cascade;"""
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    conn.close()


def countTournaments():
    """Returns the number of tournaments in the database."""
    conn = connect()
    query = """select count(t_name) as nb from tournaments;"""
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    conn.close()
    return result[0][0]


def countRegisteredPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    query = """select count(id_player) as nb from players;"""
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    conn.close()
    return result[0][0]


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    query = """select count(p_sname) as nb from players_c;"""
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    conn.close()
    return result[0][0]


def countMatches():
    """Returns the number of players currently registered."""
    conn = connect()
    query = """select count(id_match) as nb from matches;"""
    c = conn.cursor()
    c.execute(query)
    result = c.fetchall()
    conn.close()
    return result[0][0]


def registerTournament(t_name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
        f_name(str): the player's first name.
        name(str): the player's name
    """
    conn = connect()
    query = "insert into tournaments (t_name) values ({!r})"
    c = conn.cursor()
    c.execute(query.format(t_name))
    conn.commit() 
    conn.close()


def registerPlayer(f_name, name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
        f_name(str): the player's first name.
        name(str): the player's name
    """
    conn = connect()
    query = "insert into players_c (p_sname, p_name) values ({!r}, {!r})"
    c = conn.cursor()
    c.execute(query.format(f_name, name))
    conn.commit() 
    conn.close()


def getTournamentId(tournament_name):
    # get the tournament's id
    conn = connect()
    c = conn.cursor()
    query = "select id_tournament from tournaments where t_name={!r}"
    c.execute(query.format(tournament_name))
    t_id = c.fetchall()
    conn.close()
    return t_id[0][0]


def getPlayerId(p_sname, p_name):
    # get the player's id
    conn = connect()
    c = conn.cursor()
    condition = "where p_sname={!r} and p_name={!r}".format(p_sname, p_name)
    query = "select id_player_c from players_c " + condition
    c.execute(query)
    p_id = c.fetchall()
    conn.close()
    return p_id[0][0]


def registerPlayerTournament(p_id, t_id):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
        f_name(str): the player's first name.
        name(str): the player's name
    """
    # register a player in a tournament
    conn = connect()
    c = conn.cursor()
    query = """insert into players (id_player_c, tournament) values ({!r}, {!r})"""
    c.execute(query.format(p_id, t_id))
    conn.commit() 
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    # First register a tournament and players
    # get the tournament's id
    conn = connect()
    c = conn.cursor()
    # my_players = [("Melpomene", "Murray"), ("Randy", "Schwartz")]
    # insert_values = []
    # p_ids = []
    # for player in my_players:
    #     p_sname, p_name = player
    #     # registerPlayer(p_sname, p_name)

    #     # get the player's id
    #     condition = "where p_sname={!r} and p_name={!r}".format(p_sname, p_name)
    #     query = "select id_player_c from players_c " + condition
    #     c.execute(query)
    #     p_id = c.fetchall()
    #     print(p_id)
    #     p_ids.append(p_id[0][0])
        
    #     # build the insert values
    #     insert_values.append("({!r}, {!r})".format(p_id[0][0], t_id[0][0]))

    # # join all the values
    # ins = ",".join(insert_values)

    # # register the players in the tournament
    # query = "insert into players \
    # (id_player_c, tournament) values {}".format(ins)
    # c.execute(query)
    # conn.commit()
    # search for these players in the players_c table
    
    # view = """DROP VIEW playstats;
    #             CREATE VIEW playstats AS
    #             SELECT id_player, p_sname, p_name, t_name, wins, matches
    #             FROM players, players_c, tournaments
    #             WHERE players.id_player_c = players_c.id_player_c
    #             AND tournaments.id_tournament = players.tournament;"""
    # c.execute(view)
    # conn.commit()
    query = "select * from playstats;"
    c.execute(query)
    players_reg = c.fetchall()
    conn.close()
    return players_reg



def reportMatch(score_p1, score_p2, tournament, p1, p2):
    """
    MODIFIED THE FUNCTION TO RECORD THE SCORE
    Records the outcome of a single match between two players.

    Args:
        id_p1:  the id number of the player 1
        id_p2:  the id number of the player 2
        score_p1: the score of the player 1
        score_p2: the score of the player 2
        tournament: the id number of the tournament
    """
    conn = connect()
    c = conn.cursor()
    # build the inserts for the match
    assert p1 != p2, "You have to use two different player ids!"
    match_val = "({!r}, {!r}, {!r}, {!r}, {!r})".format(score_p1,
                                                        score_p2,
                                                        tournament,
                                                        p1,
                                                        p2)
    # add a new match between those 2 players
    query = "insert into matches \
    (score_p1, score_p2, tournament, id_p1, id_p2) values {}".format(match_val)

    c.execute(query)
    conn.commit()

    # update matches in the players table
    
    condition = "where id_player = {} or id_player = {};".format(p1, p2)
    query = "update players set matches = matches + 1 {}"
    c.execute(query.format(condition))
    conn.commit()

    # update wins in the player table
    if score_p1 > score_p2:
        condition = "where id_player = {};".format(p1)
        query = "update players set wins = wins + 1 {}"
        c.execute(query.format(condition))
        conn.commit()
    elif score_p2 > score_p1:
        condition = "where id_player = {};".format(p2)
        query = "update players set wins = wins + 1 {}"
        c.execute(query.format(condition))
        conn.commit()
    else:
        condition = "where id_player = {};".format(p1)
        query = "update players set wins = wins + 1 {}"

    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    conn = connect()
    c = conn.cursor()
    standings = playerStandings()
    # because the view returns players ordered by wins
    l_of_tup = []
    for i in range(0, len(standings)-1, 2):
        p1 = standings[i]
        p2 = standings[i+1]
        l_of_tup.append((p1[0], p1[1], p1[2],
                         p2[0], p2[1], p2[2]))
    return l_of_tup 
