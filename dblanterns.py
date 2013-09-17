from flask import *
from multiprocessing import Process, Pipe
from algorithm import Algorithm
from math import pi
import lanternscsv as lcsv
import repository as repo

app = Flask(__name__)
app.debug = True
#dictionary which maps problemid and Algorithm instance
#{problemid: Algorithm_inst}
alg_map = dict()

@app.before_request
def before_request():
    repo.open_connection()

@app.teardown_request
def teardown_request(exception):
    repo.close_connection()

@app.route('/')
def index():
    problemids = repo.get_all_problem_ids()
    return render_template('index.html', problemids=problemids)

@app.route('/csv/upload', methods=['POST'])
def csv_upload():
    file = request.files['csvfile']
    contents = file.read()
    lcsv.save_to_csv(contents)
    problemid = repo.create_problem(contents)
    return redirect(url_for('problem_show', problemid=problemid))

@app.route('/csv/export', methods=['POST'])
def csv_export():
    if lcsv.exportUpdatedCSVFile():
        return 'True'
    return 'False'

@app.route('/problem/show/<problemid>')
def problem_show(problemid):
    data = repo.get_data(problemid)
    points = repo.get_points_for_open_layer(problemid)
    return render_template(
        'showproblem.html',
        problemid=problemid,
        data=data,
        points=points)

@app.route('/problem/delete/<problemid>', methods=['POST'])
def problem_delete(problemid):
    repo.delete_problem(problemid)
    return redirect(url_for('index'))

@app.route('/problem/group/<problemid>', methods=['POST'])
def problem_group(problemid):
    alg_map[problemid] = Algorithm(problemid)
    alg_map[problemid].run()
    return 'Algorytm rozpoczal dzialanie...'

@app.route('/problem/group/check_status/<problemid>', methods=['POST'])
def check_status(problemid):
    result = alg_map[problemid].status()
    msg = ''
    if result and len(result) == 2:
        msg = '{"width": ' + str(result[0]) + ', "style":"' + result[1] + '"}'
    return msg

@app.route('/problem/edit/<problemid>', methods=['POST'])
def edit_grouped_problem(problemid):
    #Po wykonaniu sie algorytmu i kliknieciu przez uzytkownika sukces wyswietlamy mapke z mozliwoscia edycji rezultatow
    #dzialania algorytmu
    #Mozliwe bedzie takze przejscie do ogladania z poziomu wyswietlania problemu
    return render_template('editgroup.html', problemid=problemid)

@app.route('/group/calculate/<problemid>')
def calculate_groups(problemid):
    repo.delete_all_stripes_and_groups()

    stripe = repo.get_first_stripe(problemid)

    # stripe parameters
    stripe.width = 100
    count = 100
    step = pi / count

    # rotate the stripe and find fitting points
    for i in range(count):
        radians = i * step
        stripe = repo.rotate_stripe(stripe, radians)
        pointDicts = repo.get_points_in_stripe(problemid, stripe)
        repo.add_stripe_to_db(pointDicts)
        repo.add_group_to_db(pointDicts)

    return redirect(url_for('show_group'))

@app.route('/group/show/<groupid>')
@app.route('/group/show')
def show_group(groupid=None):
    allids = repo.get_group_ids()

    points = []
    if groupid is not None:
        points = [repo.to_openlayers_projection(p[0], p[1]) 
            for p in repo.get_points_in_group(groupid)]

    return render_template(
        'showpoints.html',
        groupids=allids,
        groupid=groupid,
        points=points)

if __name__ == '__main__':
    app.run()
