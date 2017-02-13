from app import app
from flask import g, Flask, jsonify, render_template, request, redirect, Response, url_for
from redis import StrictRedis
import time, math
import json






def get_db_campaign():
    if not hasattr(g, 'redis_db_campaign'):

    	g.redis_db_campaign = StrictRedis(host=app.config['REDIS_HOST'], password=app.config['REDIS_AUTH'], db=1)
    return g.redis_db_campaign

def get_db_cntr():
    if not hasattr(g, 'redis_db_cntr'):
        g.redis_db_cntr = StrictRedis(host=app.config['REDIS_HOST'], password=app.config['REDIS_AUTH'], db=4)
    return g.redis_db_cntr

def event_stream():
    red = get_db_campaign()  
    pubsub = red.pubsub()
    pubsub.subscribe('tored')
    for message in pubsub.listen():
        #print message
        yield 'data: %s\n\n' % message['data']



@app.route('/demo')
def demo():
    return redirect("http://www.coupio.us:8000", code=302)


@app.route('/post', methods=['POST'])
def post():
    message = flask.request.form['message']
    user = flask.session.get('user', 'anonymous')
    now = datetime.datetime.now().replace(microsecond=0).time()
    red.publish('chat', u'[%s] %s: %s' % (now.isoformat(), user, message))



@app.route('/campaigns')
def display_campaign():
    campaign_id = request.args.get('cid')
    
    red =  get_db_campaign()
    campaign_info = []
    if campaign_id is not None:
    	campaign_info = red.hgetall(campaign_id)
    else:
    	keys = red.keys('*')
	for key in keys:
    		campaign_info.append(red.hgetall(key))
    return render_template('campaign.html', result=campaign_info)


@app.route('/create')
def create_campaign():
    return render_template('create_campaign.html')


@app.route('/analytics')
def view_analytics():
    return render_template('analytics.html')

@app.route("/create", methods=['POST'])
def campaign_post():
    campaign_name = request.form["cname"]
    campaign_target = request.form["ctarget"]
    product = request.form["product"]
    promotion = request.form["promotion"]
    red =  get_db_campaign()
    red2 = get_db_cntr() 
    cnter = red2.incr("counter") 
    dict = {"campaign":campaign_name, "product":product, "promotion":promotion, "campaign_target":campaign_target, "coupon_count": 0}
    red.hmset(cnter,dict)


    return redirect(url_for('display_campaign'))



@app.route('/')
def index():
    return render_template('index.html')
 
 
