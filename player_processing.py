import sqlite3
import interaction

highscore = 1


class User:
    def __init__(self, name, highscore=1, time=0):
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
        global highscore
        con = sqlite3.connect('data/LightWar.db')
        cur = con.cursor()
        self.id, self.name, self.highscore, self.time = cur.execute("""
                                                    SELECT * FROM users WHERE username = ?
                                                """, (self.name,)).fetchall()[0]
        highscore = self.highscore
        con.commit()
        con.close()

    def update_player(self):
        con = sqlite3.connect('data/LightWar.db')
        cur = con.cursor()
        cur.execute(f"""
                        UPDATE users SET time = ? WHERE username = ?
                    """, (int(self.time + interaction.total_time), self.name)).fetchall()
        con.commit()
        con.close()

    def next_level(self):
        global highscore
        if self.highscore < 5:
            self.highscore += 1
            highscore = self.highscore
        con = sqlite3.connect('data/LightWar.db')
        cur = con.cursor()
        cur.execute(f"""
                                UPDATE users SET highscore = ? WHERE username = ?
                            """, (self.highscore, self.name)).fetchall()
        con.commit()
        con.close()
