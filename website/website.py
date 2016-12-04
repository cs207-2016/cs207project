import logging
import random
from flask import Flask, request, abort, jsonify, make_response
from flask.ext.sqlalchemy import SQLAlchemy, DeclarativeMeta
from json import JSONEncoder

logger = logging.getLogger(__name__)


class ProductJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            return obj.to_dict()
        return super(ProductJSONEncoder, self).default(obj)


app = Flask(__name__)
app.json_encoder = ProductJSONEncoder

user = 'ubuntu'
password = 'cs207password'
host = 'localhost'
port = '5432'
db = 'ubuntu'
url = 'postgresql://{}:{}@{}:{}/{}'
url = url.format(user, password, host, port, db)
app.config['SQLALCHEMY_DATABASE_URI'] = url  # 'sqlite:////tmp/tasks.db'
db = SQLAlchemy(app)


class TimeseriesEntry(db.Model):
    __tablename__ = 'timeseries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blarg = db.Column(db.Float, nullable=False)
    level = db.Column(db.String(1), nullable=False)
    mean = db.Column(db.Float, nullable=False)
    std = db.Column(db.Float, nullable=False)
    fpath = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<ID %r>' % self.id

    def to_dict(self):
        return dict(id=self.id, blarg=self.blarg, level=self.level, mean=self.mean, std=self.std, fpath=self.fpath)


@app.route('/timeseries', methods=['GET'])
def get_all_metadata():
    if 'mean_in' in request.args:
        mean_in = request.args.get('mean_in')
        # Do query
    logger.info('Getting all TimeseriesEntries')
    return jsonify(dict(tasks=TimeseriesEntry.query.all()))


@app.route('/timeseries', methods=['POST'])
def create_entry():
    if not request.json:
        abort(400)
    logger.info('Creating TimeseriesEntry')
    blarg = random.random()
    level = random.choice(["A","B","C","D","E","F"])
    #save to file and get fpath (replace with storage manager)
    fpath=""
    #Create timeseries object from json
    #get mean and std
    mean=0
    std=0
    prod = TimeseriesEntry(blarg=blarg, level=level, mean=mean, std=std, fpath=fpath)
    db.session.add(prod)
    db.session.commit()
    return jsonify({'op': 'OK', 'task': prod}), 201

@app.route('/timeseries/<int:timeseries_id>', methods=['GET'])
def get_timeseries_by_id(timeseries_id):
    ts = TimeseriesEntry.query.filter_by(id=timeseries_id).first()
    if ts is None:
        logger.info('Failed to get TimeseriesEntry with id=%s', timeseries_id)
        abort(404)
    logger.info('Getting TimeseriesEntry with id=%s', timeseries_id)
    return jsonify({'task': ts})

@app.route('/simquery', methods=['GET'])
def get_simquery():
    if 'id' in request.args:
        id = request.args.get('id')
        # run the similarity search
    else:
        abort(400)

@app.route('/simquery', methods=['POST'])
def post_simquery():
    if not request.json:
        abort(400)
    # handle post

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    db.create_all()
    app.run(port=8080)
