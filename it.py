from flask import Flask, Blueprint, render_template
from flask_restplus import Api, Resource
from flask_restplus import fields, reqparse

app = Flask(__name__)
api = Api(app = app)

app.config['UPLOAD_FOLDER'] = 'static/'

name_space = api.namespace('itask', description='IT APIs')

drink = api.model('drink', {
    'name':fields.String, 'kind':fields.String, 'hotcold':fields.String, 'price':fields.String, 'amount':fields.String
}, required = True, description = 'Drink')

pars = reqparse.RequestParser()
pars.add_argument('Name', type=str, required=True)
pars.add_argument('Kind', type=str, required=True)
pars.add_argument('Hot / Cold', type=str, required=True)
pars.add_argument('Price', type=float, required=True)
pars.add_argument('Amount', type=int, required=True)

drink_list = []

@name_space.route("/")
class MainClass(Resource):
    @name_space.doc("")
    @name_space.marshal_with(drink)
    def get(self):
        global drink_list
        if drink_list:
            return drink_list
        else:
            return 'null'

@name_space.route("/list")
class AddListClass(Resource):
    @name_space.doc("")
    @name_space.expect(pars)
    @name_space.marshal_with(drink)
    def get(self):
        global drink_list
        args = pars.parse_args()

        index = 0
        isHere = 0

        for i in drink_list:
            if i['name'] == args['Name']:
                isHere = 1
                index = drink_list.index(i)

        if isHere == 1:
            drink_list[index]['kind'] = args['Kind']
            drink_list[index]['hotcold'] = args['Hot / Cold']
            drink_list[index]['price'] = args['Price']
            drink_list[index]['amount'] = args['Amount']
        else:
            drink_list.append({'name': args['Name'], 'kind': args['Kind'], 'hotcold': args['Hot / Cold'], 'price': args['Price'], 'amount': args['Amount']})

        return drink_list

par = reqparse.RequestParser()
par.add_argument('Name', type=str, required=True)

@name_space.route('/remove')
class RemoveListClass(Resource):
    @name_space.doc("")
    @name_space.expect(par)
    @name_space.marshal_with(drink)
    def get(self):
        global drink_list
        args = par.parse_args()

        for i in drink_list:
            if i['name'] == args['Name']:
                del drink_list[drink_list.index(i)]

        return drink_list

minmax = api.model('minmax', {
    'min':fields.String, 'max':fields.String, 'field':fields.String
}, required = True, description = "Minmax")

pmm = reqparse.RequestParser()
pmm.add_argument('Name', type=str, required=True)

minmax_list = [0, 0, '']

@name_space.route('/minmax')
class MinMaxClass(Resource):
    @name_space.doc("")
    @name_space.expect(pmm)
    @name_space.marshal_with(minmax)
    def get(self):
        global drink_list
        global minmax_list

        args = pmm.parse_args()

        try:
            minmax_list[0] = drink_list[0][args['Name']]
            minmax_list[1] = 0
            minmax_list[2] = args['Name']

            for i in drink_list:
                if i[args['Name']] > minmax_list[1]:
                    minmax_list[1] = i[args['Name']]
                if i[args['Name']] < minmax_list[0]:
                    minmax_list[0] = i[args['Name']]

            return {'min':minmax_list[0], 'max':minmax_list[1], 'field':args['Name']}
        except Exception:
            minmax_list[0] = drink_list[0]['price']
            minmax_list[1] = 0
            minmax_list[2] = 'price'

            for i in drink_list:
                if i['price'] > minmax_list[1]:
                    minmax_list[1] = i['price']
                if i['price'] < minmax_list[0]:
                    minmax_list[0] = i['price']

            return {'min':minmax_list[0], 'max':minmax_list[1], 'field':args['Name']}

sort = reqparse.RequestParser()
sort.add_argument('Name', type=str, required=True)

@name_space.route('/sorted')
class SortClass(Resource):
    @name_space.doc("")
    @name_space.expect(sort)
    @name_space.marshal_with(drink)
    def get(self):
        global drink_list
        args = sort.parse_args()

        try:
            drink_list = sorted(drink_list, key=lambda k: k[args['Name']])
            return drink_list
        except Exception:
            drink_list = sorted(drink_list, key=lambda k: k['name'])
            return drink_list

user_list = []

parse_buy = reqparse.RequestParser()
parse_buy.add_argument('Name', type=str, required=True)
parse_buy.add_argument('Amount', type=int, required=True)

@name_space.route("/<int:id>")
@name_space.param('id', 'indentifier')
class UserBuyClass(Resource):
    @name_space.doc("")
    @name_space.expect(parse_buy)
    @name_space.marshal_with(drink)
    def get(self, id):
        global drink_list
        global user_list

        args = parse_buy.parse_args()
        index = -1

        calc = args['Amount']

        for i in drink_list:
            if calc > drink_list[drink_list.index(i)]['amount']:
                calc = drink_list[drink_list.index(i)]['amount']
            if i['name'] == args['Name']:
                if user_list != []:
                    for j in user_list:
                        if j[0] == id:
                            for p in j[1]:
                                if p['name'] == args['Name']:
                                    p['amount'] += calc
                                    drink_list[drink_list.index(i)]['amount'] -= calc
                                    if drink_list[drink_list.index(i)]['amount'] == 0:
                                        del drink_list[drink_list.index(i)]
                                    return p

                            cont = {
                                'name': args['Name'],
                                'kind':'',
                                'hotcold':'',
                                'price':0,
                                'amount':calc
                            }
                            j[1].append(cont)
                            index = j[1].index(cont)

                            j[1][index]['kind'] = drink_list[drink_list.index(i)]['kind']
                            j[1][index]['hotcold'] = drink_list[drink_list.index(i)]['hotcold']
                            j[1][index]['price'] = drink_list[drink_list.index(i)]['price']

                            drink_list[drink_list.index(i)]['amount'] -= calc
                            if drink_list[drink_list.index(i)]['amount'] == 0:
                                del drink_list[drink_list.index(i)]

                            return j[1]

                    cont = [id, [{
                        'name': args['Name'],
                        'kind':'',
                        'hotcold':'',
                        'price':0,
                        'amount':calc
                    }]]

                    user_list.append(cont)
                    index = user_list.index(cont)

                    user_list[index][1][0]['kind'] = drink_list[drink_list.index(i)]['kind']
                    user_list[index][1][0]['hotcold'] = drink_list[drink_list.index(i)]['hotcold']
                    user_list[index][1][0]['price'] = drink_list[drink_list.index(i)]['price']

                    drink_list[drink_list.index(i)]['amount'] -= calc
                    if drink_list[drink_list.index(i)]['amount'] == 0:
                        del drink_list[drink_list.index(i)]
                else:
                    if calc > drink_list[drink_list.index(i)]['amount']:
                        calc = drink_list[drink_list.index(i)]['amount']

                    cont = [id, [{
                        'name': args['Name'],
                        'kind':'',
                        'hotcold':'',
                        'price':0,
                        'amount':calc
                    }]]

                    user_list.append(cont)
                    index = user_list.index(cont)

                    user_list[index][1][0]['kind'] = drink_list[drink_list.index(i)]['kind']
                    user_list[index][1][0]['hotcold'] = drink_list[drink_list.index(i)]['hotcold']
                    user_list[index][1][0]['price'] = drink_list[drink_list.index(i)]['price']

                    drink_list[drink_list.index(i)]['amount'] -= calc
                    if drink_list[drink_list.index(i)]['amount'] == 0:
                        del drink_list[drink_list.index(i)]

        if index != -1:
            return user_list[index][1]
        else:
            return 'None'

@app.route('/table', methods=["GET", "POST"])
def home():
    global drink_list
    return render_template('drink_table.html', list = drink_list, mm = minmax_list)

@app.route('/table/<int:id>', methods=["GET", "POST"])
def users(id):
    global user_list

    for i in user_list:
        if i[0] == id:
            print(i[1])
            return render_template('bought_drinks.html', id=id, list=i[1])

    return 'None'

app.run(debug=True)
