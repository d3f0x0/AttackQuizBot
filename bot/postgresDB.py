import psycopg2
from pyattck import Attck

from typingBot import StaticMitre


def calculate_stat(true_answer: int | None, all_answer: int | None) -> int:
    if all_answer == 0 or (all_answer is None or true_answer is None):
        return 0
    return int((true_answer / all_answer) * 100)


class DataBase:
    def __init__(self, dbname, user, password, host, port) -> None:
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = psycopg2.connect(database=self.dbname, user=self.user, password=self.password,
                                     host=self.host, port=self.port)
        self.cur = self.conn.cursor()

    def generate_data(self) -> None:
        print("INFO - Download Attack files")
        attack = Attck()
        print(f"INFO - Started insert date to database")
        for tactic in attack.enterprise.tactics:
            with self.conn:
                with self.conn.cursor() as cur:
                    cur.execute(f"INSERT INTO tactics (id_t, name, description) VALUES (%s, %s, %s) "
                                f"ON CONFLICT (id_t, name) DO UPDATE SET description=excluded.description;",
                                [tactic.external_references[0].external_id, tactic.name, tactic.description])

            for tech in tactic.techniques:
                with self.conn:
                    with self.conn.cursor() as cur:
                        cur.execute(f"INSERT INTO techniques (id_ta, name, description, id_tactics)"
                                    f"VALUES (%s, %s, %s, %s) ON CONFLICT (id_ta, name, id_tactics) "
                                    f"DO UPDATE SET description=excluded.description;",
                                    [tech.external_references[0].external_id, tech.name, tech.description,
                                     tactic.external_references[0].external_id])

                for mitigation in tech.mitigations:
                    if mitigation:
                        with self.conn:
                            with self.conn.cursor() as cur:
                                cur.execute(f"INSERT INTO mitigations (id_mt, name, description, id_tech)"
                                            f"VALUES (%s, %s, %s, %s) ON CONFLICT (id_mt, id_tech, name) "
                                            f"DO UPDATE SET description=excluded.description",
                                            [mitigation.external_references[0].external_id, mitigation.name,
                                             mitigation.description, tech.external_references[0].external_id])

        self.conn.commit()
        print("Successful data generate")

    def insert_users(self, user_id, user_name, last_update) -> None:
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(f"INSERT INTO users (id_user, name, last_date) VALUES (%s, %s, %s) "
                            f"ON CONFLICT (id_user, name) DO UPDATE SET last_date=EXCLUDED.last_date;",
                            [user_id, user_name, last_update])
        self.conn.commit()

    def insert_stat(self, user_id, mitre_id, true_poll_answer, poll_id) -> None:
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO statistics (id_user, mitre_id, true_poll_answer, poll_id) "
                            "VALUES (%s, %s, %s, %s) ON CONFLICT (id_user, mitre_id) DO UPDATE "
                            "SET (poll_id, true_poll_answer)=(EXCLUDED.poll_id, EXCLUDED.true_poll_answer)",
                            [user_id, mitre_id, true_poll_answer, poll_id])
        self.conn.commit()

    def update_stat(self, poll_answer, poll_id) -> None:
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(f"SELECT true_answers, true_poll_answer, count FROM statistics "
                            f"WHERE poll_id = '{poll_id}';")
                result_select = cur.fetchall()

                if int(poll_answer) == int(result_select[0][1]):
                    cur.execute(
                        f"UPDATE statistics SET true_answers = true_answers + 1, count = count + 1"
                        f"WHERE poll_id='{poll_id}';")
                else:
                    cur.execute(
                        f"UPDATE statistics SET count = count + 1 WHERE poll_id='{poll_id}';")
        self.conn.commit()

    def select_stat(self, user_id: int) -> StaticMitre:
        self.cur.execute("SELECT SUM(statistics.count) AS total_count, sum(statistics.true_answers) as total_true"
                         " FROM statistics;")
        total_count = self.cur.fetchall()
        self.cur.execute(f"select sum(statistics.count) as total_count, sum(statistics.true_answers) as total_true "
                         f"from statistics where mitre_id similar to 'T(1|2)%' and id_user ='{user_id}';")
        total_tech = self.cur.fetchall()
        self.cur.execute(f"select sum(statistics.count) as total_count, sum(statistics.true_answers) as total_true "
                         f"from statistics where mitre_id similar to 'TA%' and id_user ='{user_id}';")
        total_tactic = self.cur.fetchall()
        self.cur.execute(f"select sum(statistics.count) as total_count, sum(statistics.true_answers) as total_true "
                         f"from statistics where mitre_id similar to 'M%' and id_user ='{user_id}';")
        total_mitigations = self.cur.fetchall()

        tactics = calculate_stat(total_tactic[0][1], total_tactic[0][0])
        techniques = calculate_stat(total_tech[0][1], total_tech[0][0])
        mitigations = calculate_stat(total_mitigations[0][1], total_mitigations[0][0])
        all_stat = calculate_stat(total_count[0][1], total_count[0][0])

        return StaticMitre(tactics, techniques, mitigations, all_stat)

    def select_tactics(self, t_name: str = None, t_id: str = None) -> list:
        if t_name is None and t_id is None:
            self.cur.execute("SELECT id_t, name, description FROM tactics order by random()  limit 4;")
        elif t_name is not None:
            self.cur.execute(f"SELECT id_t, name, description FROM tactics WHERE name LIKE '{t_name}' "
                             f"order by random()  limit 4;")
        elif t_id is not None:
            self.cur.execute(f"SELECT id_t, name, description FROM tactics WHERE id_t LIKE '{t_id}' "
                             f"order by random()  limit 4;")
        tactics = self.cur.fetchall()
        return tactics

    def select_techniques(self, t_name: str = None, t_id: int = None, id_tactics: str = None) -> list:
        if t_name is None and t_id is None and id_tactics is None:
            self.cur.execute("SELECT id_ta, name, description, id_tactics FROM techniques "
                             "order by random()  limit 4;")
        elif t_name is not None:
            self.cur.execute(f"SELECT id_ta, name, description, id_tactics FROM techniques "
                             f"WHERE name LIKE '{t_name}' order by random()  limit 4;")
        elif t_id is not None:
            self.cur.execute(f"SELECT id_ta, name, description, id_tactics FROM techniques "
                             f"WHERE id_ta LIKE '{t_id}' order by random()  limit 4;")
        elif id_tactics is not None:
            self.cur.execute(f"SELECT id_ta, name, description, id_tactics FROM techniques "
                             f"WHERE id_tactics LIKE '{id_tactics}' order by random()  limit 4;")
        techniques = self.cur.fetchall()
        return techniques

    def select_mitigations(self, mt_name: str = None, mt_id: str = None) -> list:
        """Get mitigations from database. Return tuple"""
        if mt_name is None and mt_id is None:
            self.cur.execute("SELECT id_mt, name, description FROM mitigations order by random()  limit 4;")
        elif mt_name is not None:
            self.cur.execute(f"SELECT id_mt, name, description FROM mitigations WHERE name LIKE '{mt_name}' "
                             f"order by random()  limit 4;")
        elif mt_id is not None:
            self.cur.execute(f"SELECT id_mt, name, description FROM mitigations WHERE id_mt LIKE '{mt_id}' "
                             f"order by random()  limit 4;")
        mitigations = self.cur.fetchall()
        return mitigations


if __name__ == "__main__":
    print("Sorry, i'm module")
