import sqlite3
import interaction

total_highscore = 1


# Класс, реализующий работу с базой данных пользователей
class User:
    def __init__(self, name, highscore=1, time=0):
        self.id = None
        self.name = name
        self.highscore = highscore
        self.time = time

    # Добавление нового пользователя в базу данных
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
        finally:
            return self.highscore

    # Подгрузка данных уже существующего пользователя
    def upload_player(self):
        global total_highscore
        con = sqlite3.connect('data/LightWar.db')
        cur = con.cursor()
        self.id, self.name, self.highscore, self.time = cur.execute("""
                                                    SELECT * FROM users WHERE username = ?
                                                """, (self.name,)).fetchall()[0]
        total_highscore = self.highscore
        con.commit()
        con.close()

    # Обновление данных пользователя в базе данных
    def update_player(self):
        if self.highscore < 6:
            con = sqlite3.connect('data/LightWar.db')
            cur = con.cursor()
            cur.execute(f"""
                            UPDATE users SET time = ? WHERE username = ?
                        """, (int(self.time + interaction.total_time), self.name)).fetchall()
            con.commit()
            con.close()

    # Информация о том, что пользователь перешёл на новый уровень
    def next_level(self, win_cek):
        global total_highscore
        if self.highscore < 6:
            self.highscore += win_cek

            total_highscore = self.highscore
            con = sqlite3.connect('data/LightWar.db')
            cur = con.cursor()
            cur.execute(f"""
                            UPDATE users SET highscore = ? WHERE username = ?
                         """, (self.highscore, self.name)).fetchall()
            con.commit()
            con.close()

    # Получение актуальной сложности для конкретного пользователя
    def get_highscore(self):
        return self.highscore
