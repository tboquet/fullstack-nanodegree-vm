#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach




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
    """Adds a tournament to the tournament table.

    The database assigns a unique serial id number for the tournament.

    Args:
        t_name(str): the tournament's name.
    """
    conn = connect()
    t_name = bleach.clean(t_name)
    query = "insert into tournaments (t_name) values (%s)"
    c = conn.cursor()
    c.execute(query, (t_name,))
    conn.commit() 
    conn.close()


def registerPlayer(f_name, name):
    """Adds a player to the player_c table.

    The database assigns a unique serial id number for the player.

    Args:
        f_name(str): the player's first name.
        name(str): the player's name
    """
    conn = connect()
    f_name = bleach.clean(f_name)
    name = bleach.clean(name)
    query = "insert into players_c (p_sname, p_name) values (%s, %s)"
    c = conn.cursor()
    c.execute(query, (f_name, name))
    conn.commit() 
    conn.close()


def getTournamentId(tournament_name):
    """Utility function to retrieve a tournament id using its name

    Args:
        tournament_name(str): the name of the tournament

    Returns:
        the unique id of a tournament (int).

    .. note::
        We take the first tournament we find in the db!!!"""

    # get the tournament's id
    conn = connect()
    c = conn.cursor()
    tournament_name = bleach.clean(tournament_name)
    query = "select id_tournament from tournaments where t_name=%s"
    c.execute(query, (tournament_name,))
    t_id = c.fetchall()
    conn.close()
    return t_id[0][0]


def getPlayerId(p_sname, p_name):
    """Utility function to retrieve a player id using his first and last names

    Args:
        p_sname(str): the first name of the player
        p_name(str): the last name of the player

    Returns:
        the unique id of a player from the players_c table (int).

    .. note::
        We take the first player we find in the db!!!"""

    # get the player's id
    conn = connect()
    c = conn.cursor()
    p_sname = bleach.clean(p_sname)
    p_name = bleach.clean(p_name)
    condition = "where p_sname=%s and p_name=%s"
    query = "select id_player_c from players_c " + condition
    c.execute(query, (p_sname, p_name))
    p_id = c.fetchall()
    conn.close()
    return p_id[0][0]


def registerPlayerTournament(p_id, t_id):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player, tournament
    pair. We use the player id from the players_c table and the tournament
    id from the tournaments table.

    Args:
        p_id(int): the player's unique id from the players_c table.
        t_id(int): the tournament's unique id from the tournaments table 
    """
    # register a player in a tournament
    conn = connect()
    c = conn.cursor()
    # no need to clean because we get this data from the db
    query = """insert into players (id_player_c, tournament) values (%s, %s)"""
    c.execute(query, (p_id, t_id))
    conn.commit() 
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, p_sname, p_name, tournament
                                                wins, matches, tournament_id):
        id(int): the player's unique id (assigned by the database)
        p_sname(str): the player's first name (as registered)
        p_name(str): the player's last name (as registered)
        wins(int): the number of matches the player has won
        matches(int): the number of matches the player has played
    """

    conn = connect()
    c = conn.cursor()
    query = "select * from playstats;"
    c.execute(query)
    players_reg = c.fetchall()
    conn.close()
    return players_reg


def reportMatch(score_p1, score_p2, tournament, p1, p2):
    """
    Records the outcome of a single match between two players.

    Args:
        id_p1(int):  the id number of the player 1
        id_p2(int):  the id number of the player 2
        score_p1(int): the score of the player 1
        score_p2(int): the score of the player 2
        tournament(int): the id number of the tournament
    """
    conn = connect()
    c = conn.cursor()
    # build the inserts for the match
    assert p1 != p2, "You have to use two different player ids!"
    match_val = "(%s, %s, %s, %s, %s)"
    # add a new match between those 2 players
    query = "insert into matches \
    (score_p1, score_p2, tournament, id_p1, id_p2) values " + match_val

    c.execute(query, (score_p1, score_p2, tournament, p1, p2))
    conn.commit()

    # update matches variable in the players table
    
    condition = "where id_player = {} or id_player = {};".format(p1, p2)
    query = "update players set matches = matches + 1 {}"
    c.execute(query.format(condition))
    conn.commit()

    # update wins variable in the players table
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
    conn.close()


def swissPairingsPython():
    """Returns a list of pairs of players for the next round of a match.
    USING PYTHON!
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1(int): the first player's unique id
        p_sname1(str): the first player's first name
        p_sname1(str): the first player's last name
        id2(int): the second player's unique id
        p_sname2(str): the second player's first name
        p_sname1(str): the second player's last name
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


def swissPairingsSQL():
    """Returns a list of pairs of players for the next round of a match.
    USING A VIEW IN THE DATABASE!
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1(int): the first player's unique id
        p_sname1(str): the first player's first name
        p_sname1(str): the first player's last name
        id2(int): the second player's unique id
        p_sname2(str): the second player's first name
        p_sname1(str): the second player's last name
    """

    conn = connect()
    c = conn.cursor()
    query = "select * from pairing"
    c.execute(query)
    pairing = c.fetchall()
    conn.close
    return pairing
