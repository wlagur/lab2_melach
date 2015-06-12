from flask import Flask
import json
import requests
from flask import render_template, request
from flask import redirect
from flask_wtf import Form
from wtforms import StringField
from wtforms import DateField
from wtforms import IntegerField
from wtforms import SubmitField
from neo4j import import_api_data

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

#region initialisation
app = Flask(__name__)

app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key='cb165d954518c4e5f620',
    consumer_secret='8350c5084bfeb3879f2f90fa13aeb88a307fe3c3',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

WTF_CSRF_ENABLED = False
#endregion

# region Form
class DemandForm(Form):
    # id = IntegerField('id')
    sum = IntegerField('sum')
    debtor = IntegerField('Debtor')
    creditor = IntegerField('Creditor')
    # creation_date = DateField('creation_date')
    # approval_date = DateField('approval_date')
    submit = SubmitField('submit')
# endregion

# region API routing
@app.route('/')
def index():
    form = DemandForm(csrf_enabled=False)
    r = requests.get('http://127.0.0.1:5010/api/demand')
    data = json.loads(r.text)
    #print(r.text)
    if 'github_token' in session:
        return render_template('authorized.html', objects=data["objects"], form=form)
    return render_template('unauthorized.html', objects=data["objects"], form=form)

@app.route('/delete/<int:demand_id>')
def delete(demand_id):
    r = requests.delete('http://127.0.0.1:5010/api/demand/' + str(demand_id))
    #import_api_data()
    return index()


@app.route('/update/<int:demand_id>')
def update(demand_id):
    form = DemandForm(csrf_enabled=False)
    r = requests.get('http://127.0.0.1:5010/api/demand/'+str(demand_id))
    data = json.loads(r.text)
    #print(r.text)
    return render_template('update.html', demand=data, form=form)


@app.route('/send_update/<int:demand_id>', methods=['POST'])
def send_update(demand_id):
    sum = int(request.form['sum'])
    debtor_id = int(request.form['debtor'])
    creditor_id = int(request.form['creditor'])
    # creation_date = request.form['creation_date']
    # approval_date = request.form['approval_date']
    header = {'Content-Type':'application/json'}
    data = json.dumps({
                       "sum": sum,
                       "debtor_id":debtor_id,
                       "creditor_id":creditor_id})

    print(data)
    r = requests.patch('http://127.0.0.1:5010/api/demand/' + str(demand_id), data=data, headers=header)
    # r = requests.patch('http://127.0.0.1:5010/api/method/' + str(method_id))
    # r._content =
    #import_api_data()
    return index()


@app.route('/add', methods=['POST'])
def add():
    sum = int(request.form['sum'])
    debtor_id = int(request.form['debtor'])
    creditor_id = int(request.form['creditor'])
    # creation_date = request.form['creation_date']
    # approval_date = request.form['approval_date']
    header = {'Content-Type':'application/json'}
    data = json.dumps({"sum": sum,
                       "debtor_id":debtor_id,
                       "creditor_id":creditor_id})
    r = requests.post('http://127.0.0.1:5010/api/demand', headers=header, data=data)
    #import_api_data()
    return index()
# endregion

# region OAuth routing
@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


@app.route('/auth')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['github_token'] = (resp['access_token'], '')
    me = github.get('user')
    return index()


@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')
#endregion

#region PDF

@app.route('/print')
def print_form():
    r = requests.get('http://127.0.0.1:5010/api/demand')
    demand_data = json.loads(r.text)
    r = requests.get('http://127.0.0.1:5010/api/debtor')
    debtor_data = json.loads(r.text)
    r = requests.get('http://127.0.0.1:5010/api/creditor')
    creditor_data = json.loads(r.text)
    return render_template('print.html',
                           demands=demand_data["objects"],
                           debtors=debtor_data["objects"],
                           creditors=creditor_data["objects"])

# @app.route('/pdf/<string:name>')
# def generate_pdf(name):
#     pdfkit.from_url('http://127.0.0.1:5000/print', name + ".pdf")
#     return name + ".pdf generated"

#endregion

if __name__ == '__main__':
    app.run()
