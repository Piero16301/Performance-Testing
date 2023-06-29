import psycopg2

conn = psycopg2.connect(database="coviddb",
                        host="localhost",
                        user="postgres",
                        password="postgres",
                        port="5432")

if __name__ == '__main__':
    # ['0', 'Afghanistan', 'AFG', '2021-05-11', '504502.0', '448878.0', '55624.0', '12', '40374668.0',
    # '1.1117812783005423\n']
    rows = []
    with open('covid-vaccination-vs-death_ratio.csv', 'r') as f:
        f.readline()
        for line in f:
            rows.append(line.split(','))
            rows[-1][-1] = rows[-1][-1][:-1]
            rows[-1][4] = rows[-1][4][:-2]
            rows[-1][5] = rows[-1][5][:-2]
            rows[-1][6] = rows[-1][6][:-2]
            rows[-1][8] = rows[-1][8][:-2]
            cur = conn.cursor()
            cur.execute("INSERT INTO pais (country, iso_code, population) "
                        "VALUES (%s, %s, %s) "
                        "ON CONFLICT (iso_code) DO NOTHING", (rows[-1][1], rows[-1][2], rows[-1][8]))
            conn.commit()

            cur.execute("SELECT id FROM pais WHERE iso_code = %s", (rows[-1][2],))
            id_pais = cur.fetchone()[0]

            cur.execute("INSERT INTO reporte (country_id, date_issue, total_vaccinations, people_vaccinated, "
                        "people_fully_vaccinated, new_deaths, ratio)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s) ", (id_pais, rows[-1][3], rows[-1][4], rows[-1][5],
                                                                 rows[-1][6], rows[-1][7], rows[-1][9]))
            conn.commit()
            cur.close()
