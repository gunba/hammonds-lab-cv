import shutil
import jsonpickle as jp
import os
import pyodbc
import time
from cv.classes.data_wrapper import *
from multiprocessing.dummy import Pool as ThreadPool

pool = ThreadPool(16)

def create_cursor():
    conn = pyodbc.connect('DRIVER=%s;SERVER=%s;Trusted_Connection=yes;' % (c.DRIVER, c.SERVER), database=c.DATABASE)
    return conn, conn.cursor()

def upload_data():
    def convert_data():
        rounds = list()

        for filename in os.listdir(c.LAB_UPLOAD):
            with open(os.path.join(c.LAB_UPLOAD, filename)) as file:

                fight_start_index = 0

                json = jp.decode(file.read())

                round = None

                for idx, event in enumerate(json):
                    if type(event) == EventMapLoaded:
                        round = Round(event.map, event.left_team, event.right_team, event.region, event.patch, event.video, event.created)
                    elif type(event) == EventFightStart:
                        fight_start_index = idx
                    elif type(event) == EventFightEnd:
                        round.fights.append(Fight(event, json[fight_start_index:idx + 1]))

                rounds.append(round)

        return rounds

    data = convert_data()

    print('Importing data to the cloud..')

    start_time = time.time()

    def upload_data_thread(round):

        conn, cursor = create_cursor()

        print("ROUND INSERTS " + str(time.time()))

        count_fight = 0
        count_killfeed = 0

        f_execute = "DECLARE @PK_ROUND TABLE (ID INT)"
        f_execute += "\nINSERT INTO rounds (map, left_team, right_team, region, patch, video, created) OUTPUT Inserted.id into @PK_ROUND VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (round.map, round.left_team, round.right_team, round.region, round.patch, round.video, round.created)

        print("FIGHT INSERTS " + str(time.time()))
        for fight in round.fights:
            f_execute += "\nDECLARE @PK_FIGHT_%s TABLE (ID INT)" % count_fight
            f_execute += "\nINSERT INTO fights (winner, left_side, right_side, objective, frames, round, first, last) OUTPUT Inserted.id into @PK_FIGHT_%s VALUES (%s, %s, %s, %s, %s, (SELECT ID FROM @PK_ROUND), %s, %s)" % (count_fight, fight.winner, fight.left_side, fight.right_side, fight.objective, fight.fight_start.frames, fight.fight_start.gametime, fight.fight_end.gametime)

            print("SNAPSHOT INSERTS " + str(time.time()))
            for player in fight.fight_start.slots:
                f_execute += "\nINSERT INTO snapshots (type, name, hero, ult, state, team, slot, fight) VALUES (0, '%s', '%s', '%s', '%s', %s, %s, (SELECT ID FROM @PK_FIGHT_%s))" % (player.name, player.hero, player.ult, player.state, player.team, player.slot, count_fight)

            for player in fight.fight_end.slots:
                f_execute += "\nINSERT INTO snapshots (type, name, hero, ult, state, team, slot, fight) VALUES (1, '%s', '%s', '%s', '%s', %s, %s, (SELECT ID FROM @PK_FIGHT_%s))" % (player.name, player.hero, player.ult, player.state, player.team, player.slot, count_fight)

            print("KILLFEED INSERTS " + str(time.time()))
            for event in fight.killfeed_events:
                t_entity = event.entity or 'NULL'
                f_execute += "\nDECLARE @PK_KILLFEED_%s TABLE (ID INT)" % count_killfeed
                f_execute += "\nINSERT INTO killfeed_events (type, left_slot, left_name, left_hero, left_team, left_ult, left_num, ability, critical, entity, right_slot, right_name, right_hero, right_team, right_ult, right_num, gametime, frames, fight) OUTPUT Inserted.id into @PK_KILLFEED_%s " \
                             "VALUES ('%s', %s, '%s', '%s', '%s', '%s', %s, '%s', %s, '%s', %s, '%s', '%s', '%s', '%s', %s, %s, %s, (SELECT ID FROM @PK_FIGHT_%s))" \
                                 % (count_killfeed, event.type, event.left_slot, event.left_name, event.left_hero, event.left_team, event.left_ult, event.left_num, event.ability, event.critical,
                                    t_entity, event.right_slot, event.right_name, event.right_hero, event.right_team, event.right_ult, event.right_num, event.gametime, event.frames, count_fight)

                for assist in event.assists:
                    f_execute += "\nINSERT INTO assists (name, hero, ult, slot, event) VALUES ('%s', '%s', '%s', '%s', (SELECT ID FROM @PK_KILLFEED_%s))" % (assist.name, assist.hero, assist.ult, assist.slot, count_killfeed)

                count_killfeed += 1

            print("HEROBAR INSERTS " + str(time.time()))
            for event in fight.herobar_events:
                t_value = "'" + str(event.value) + "'" if event.value else 'NULL'
                f_execute += "\nINSERT INTO herobar_events (type, name, hero, slot, team, left_num, right_num, value, gametime, frames, fight) VALUES ('%s', '%s', '%s', %s, '%s', %s, %s, %s, %s, %s, (SELECT ID FROM @PK_FIGHT_%s))" \
                             % (event.type, event.name, event.hero, event.slot, event.team, event.team_num, event.enemy_num, t_value, event.gametime, event.frames, count_fight)

            print(f_execute)

            count_fight += 1

        cursor.execute(f_execute)
        conn.commit()
        conn.close()

    pool.map(upload_data_thread, data)

    #Update our generated tables.
    update_all_pd()
    cleanup_dir()

    end_time = time.time() - start_time
    print("Finished upload in " + str(end_time) + " seconds.")

def update_all_pd():
    conn, cursor = create_cursor()
    cursor.execute("exec CreateAllPd")
    conn.commit()
    conn.close()

def cleanup_dir():
    print('Deleting upload path: ' + c.LAB_UPLOAD)
    shutil.rmtree(c.LAB_UPLOAD)




