import sqlite3
import interaction


class User:
    def __init__(self, name, highscore=1, time=0):
        global total_time
        self.id = None
        self.name = name
        self.highscore = highscore
        self.time = time

    def add_player(self):
        try:
            con = sqlite3.connect('data/LightWar.db')
            cur = con.cursor()
            cur.execute("""
                            INSERT INTO users(username, highscore, time)
                            VALUES (?, ?, ?)
                        """, (self.name, self.highscore, self.time)).fetchall()
            con.commit()
            con.close()
        except sqlite3.IntegrityError:
            self.upload_player()

    def upload_player(self):
        con = sqlite3.connect('data/LightWar.db')
        cur = con.cursor()
        self.id, self.name, self.highscore, self.time = cur.execute("""
                                                    SELECT * FROM users WHERE username = ?
                                                """, (self.name, )).fetchall()[0]
        con.commit()
        con.close()

    def update_player(self):
        print(interaction.total_time)
        con = sqlite3.connect('data/LightWar.db')
        cur = con.cursor()
        cur.execute(f"""
                        UPDATE users SET time = ? WHERE username = ?
                    """, (int(self.time + interaction.total_time), self.name)).fetchall()
        con.commit()
        con.close()
