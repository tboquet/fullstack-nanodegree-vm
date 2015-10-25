#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testDeleteTournaments():
    deleteTournaments()
    print "1.a) Old tournaments can be deleted."


def testDeleteMatches():
    deleteMatches()
    print "1.c) Old matches can be deleted."


def testDeletePlayersC():
    deleteMatches()
    deletePlayersC()
    print "1.d) Player records can be deleted."


def testDeletePlayers():
    deleteMatches()
    deletePlayers()
    print "1.e) Registered player records can be deleted."


def testCountPlayers():
    deleteMatches()
    deletePlayersC()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "2.a) After deleting, countPlayers() returns zero."


def testCountRegisteredPlayers():
    deleteMatches()
    deletePlayers()
    deletePlayersC()
    c = countRegisteredPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "2.b) After deleting, countPlayers() returns zero."


def testCountTournaments():
    deleteMatches()
    deletePlayersC()
    deleteTournaments()
    deletePlayers()
    c = countTournaments()
    if c == '0':
        raise TypeError(
            "countTournaments() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countTournaments should return zero.")
    print "2.c) After deleting, countTournaments() returns zero."


def testRegisterTournament():
    deleteTournaments()
    deleteMatches()
    deletePlayersC()
    registerTournament("Magicsuper")
    c = countTournaments()
    if c != 1:
        raise ValueError(
            "After one tournament is saved, countTournaments() should be 1.")
    print "4. After registering a tournament, countTournaments() returns 1."


def testRegisterPlayerTournament():
    deleteTournaments()
    deleteMatches()
    deletePlayersC()
    registerPlayerTournament("Chandra", "Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDeletePlayer():
    deleteMatches()
    deletePlayersC()
    registerPlayer("Markov", "Chaney")
    registerPlayer("Joe", "Malik")
    registerPlayer("Mao", "Tsu-hsi")
    registerPlayer("Atlanta", "Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayersC()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testRegisterPlayer():
    deleteMatches()
    deletePlayersC()
    registerPlayer("Chandra", "Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDeletePlayer():
    deleteMatches()
    deletePlayers()
    deletePlayersC()
    registerPlayer("Markov", "Chaney")
    registerPlayer("Joe", "Malik")
    registerPlayer("Mao", "Tsu-hsi")
    registerPlayer("Atlanta", "Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayersC()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    deletePlayersC()
    deleteTournaments()
    registerTournament("supertour")
    registerPlayer("Melpomene", "Murray")
    registerPlayer("Randy", "Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 6:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, p_sname1, p_name1, tournament, wins1, matches1),
     (id2, p_sname2, p_name2, tournament, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    p1_n = [p_sname1, p_name1]
    p2_n = [p_sname2, p_name2]
    fullnames = set([" ".join(p1_n), " ".join(p2_n)])
    if fullnames != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings,"
                         " even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


if __name__ == '__main__':
    testDeletePlayers()
    testDeletePlayersC()
    testDeleteTournaments()
    testDeleteMatches()
    testCountTournaments()
    testCountPlayers()
    testCountRegisteredPlayers()
    testRegisterPlayer()
    testRegisterTournament()
    testRegisterPlayerTournament()
    testRegisterCountDeletePlayer()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"


