import sqlite3, yaml

class Database:
    def __init__(self):
        con = sqlite3.connect('data/database.db')
        # con.set_trace_callback(print) # Useful for debugging
        self.con = con
        cur = con.cursor()
        self.cur = cur
        with open("snowmed/snowmed.yaml", 'r') as stream:
            self.snowmed = yaml.safe_load(stream)

    def map_snomed_ct(self, abbr) -> dict:
        for s in self.snowmed:
            if s['abbr'] == abbr:
                return s

    def close_connection(self):
        self.con.close()

    def setup_prescription_database(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS medications (id integer, agent text, indication text)')

    def setup_laboratory_database(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS laboratory (id integer, parameter text, value integer)')

    def setup_medical_history_database(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS medical (id integer, sctid integer, term text)')

    def insert_prescription(self, id, agent, reason):
        self.cur.execute(f'INSERT INTO medications VALUES (?,?,?)', (id, agent, reason))
        self.con.commit()

    def insert_medical_history(self, id, abbreviation):
        snowmed = self.map_snowmed_ct(abbreviation)
        self.cur.execute(f'INSERT INTO medical VALUES (?,?,?)', (id, snowmed['sctid'], snowmed['term']))
        self.con.commit()