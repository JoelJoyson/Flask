from flask import jsonify, Flask,request
from flask_sqlalchemy import SQLAlchemy
from .flask_logs import LogModule
from datetime import datetime
import pymysql,json,os,logging,sys
#the below line because mysqlclient and MySQL-python fail on 3.8
pymysql.install_as_MySQLdb()

app=Flask(__name__)

# File Logging Setup
app.config["filename"] = os.path.basename(sys.argv[0]).split(".")[0]+".log"
app.config["subject"] = 'SensorApp'
app.config["to_address"]=os.environ["TO_ADDRESS"]
logs = LogModule()
logs.init_app(app)

logger = logging.getLogger()

#set up the sql configs
mysql_creds=json.loads(os.environ["CONN"])
app.config['SQLALCHEMY_DATABASE_URI']=f"mysql://{mysql_creds['user']}:{mysql_creds['password']}@{mysql_creds['host']}:3306/{mysql_creds['database']}"
db=SQLAlchemy(app)



"""
The below class is the ORM for the test table
"""

class Sample(db.Model):
    __tablename__="test"
    id=db.Column(db.Integer,primary_key=True)
    sensor_id=db.Column(db.String(100),nullable=False)
    created_at=db.Column(db.DateTime,nullable=False,default=datetime.now)
    updated_at=db.Column(db.DateTime,nullable=False,default=datetime.now)
    most_recent=db.Column(db.String(10),nullable=False)

db.create_all()

@app.route('/update',methods=['POST'])
def update():
    try:
        data=request.get_json()
        sensor_id=data['sensor_id']
        db.session.query(Sample).filter(Sample.sensor_id==sensor_id,Sample.most_recent=='Yes').update({Sample.updated_at:datetime.now()})
        db.session.query(Sample).filter(Sample.sensor_id==sensor_id,Sample.most_recent=='Yes').update({Sample.most_recent:'No'})
        db.session.add(Sample(sensor_id=sensor_id,most_recent='Yes'))
        db.session.commit()
        return jsonify("Data updated"),200
        
    except Exception as e:
        db.session.rollback()
        logger.exception(e)
        return issue(e.with_traceback,e)

@app.route('/select/<sensor>',methods=['GET'])
def select(sensor):
    try:
        get_data=Sample.query.filter_by(sensor_id=sensor, most_recent='Yes').first_or_404()
        return {'sensor':get_data.sensor_id}
    except Exception as e:
        logger.exception(e)
        return missing(e)


@app.after_request
def after_request(response):
    #Log after every request
    logger = logging.getLogger("app.access")
    logger.info(
        "%s [%s] %s %s %s %s %s %s %s",
        request.remote_addr,
        datetime.now().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
        request.method,
        request.path,
        request.scheme,
        response.status,
        response.content_length,
        request.referrer,
        request.user_agent,
    )
    return response


@app.errorhandler(400)
def issue(e=None,e1=None):
    message={'status':400,'message':'Client Side error:'+str(e)+":"+str(e1)}
    return jsonify(message),400

@app.errorhandler(404)
def missing(e=None):
    message={'status':404,'message':'Data Not Found for this Sensor'}
    return jsonify(message),404




