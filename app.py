import flask
import sqlalchemy
import flask_sqlalchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/coviddb'
db = flask_sqlalchemy.SQLAlchemy(app)


class Pais(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), unique=True, nullable=False)
    iso_code = db.Column(db.String(3), unique=True, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    reportes = db.relationship('Reporte', backref='pais', lazy=True)


class Reporte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=False)
    date_issue = db.Column(db.Date, nullable=False)
    total_vaccinations = db.Column(db.Integer, nullable=False)
    people_vaccinated = db.Column(db.Integer, nullable=False)
    people_fully_vaccinated = db.Column(db.Integer, nullable=False)
    new_deaths = db.Column(db.Integer, nullable=False)
    ratio = db.Column(db.Float, nullable=False)


# retrieve the content from db


@app.route('/')
def index():
    return 'Hello world'


# POST - Inserta un nuevo reporte de vacunación.
@app.route('/covid/insert', methods=['POST'])
def insert_report():
    data = flask.request.get_json()
    id_country = Pais.query.filter_by(country=data['country']).first().id
    reporte = Reporte(country_id=id_country,
                      date_issue=data['date_issue'],
                      total_vaccinations=data['total_vaccinations'],
                      people_vaccinated=data['people_vaccinated'],
                      people_fully_vaccinated=data['people_fully_vaccinated'],
                      new_deaths=data['new_deaths'],
                      ratio=data['ratio'])
    db.session.add(reporte)
    db.session.commit()
    return flask.jsonify({'inserted': True})


# GET - Devuelve el número de vacunados y nuevas muertes ordenado ascendentemente por fecha de un País.
@app.route('/covid/country/<country>', methods=['GET'])
def get_report(country):
    id_country = Pais.query.filter_by(country=country).first().id
    reportes = Reporte.query.filter_by(country_id=id_country).order_by(Reporte.date_issue).all()
    return flask.jsonify({'country': country, 'report': [
        {'vaccinated': e.total_vaccinations,
         'deaths': e.new_deaths,
         'date': e.date_issue.strftime('%Y-%m-%d')
         } for e in reportes]})


# GET - Devuelve el número de vacunados y nuevas muertes ordenado ascendentemente por fecha en un año específico.
@app.route('/covid/year/<year>', methods=['GET'])
def get_report_year(year):
    reportes = Reporte.query.filter(sqlalchemy.extract('year', Reporte.date_issue) == year).order_by(
        Reporte.date_issue).all()
    return flask.jsonify({'year': year, 'report': [
        {'vaccinated': e.total_vaccinations,
         'new_deaths': e.new_deaths,
         'date': e.date_issue.strftime('%Y-%m-%d')
         } for e in reportes]})


if __name__ == '__main__':
    app.run(debug=False, host='localhost', port=8080)
