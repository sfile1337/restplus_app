from flask import Flask, Blueprint
from flask_restplus import Api, Resource, fields, reqparse
from random import random

app = Flask(__name__)
api = Api(app=app)

# описание главного блока нашего API http://127.0.0.1:5000/main/.
name_space = api.namespace('main', description='Main APIs')

@name_space.route("/")
class MainClass(Resource):
    def get(self):
        return {"status": "Got new data"}

    def post(self):
        return {"status": "Posted new data"}

# определение модели данных массива
list_ = api.model('list', {
    'len': fields.String(required=True, description='Size of array'),
    'array': fields.List(fields.String, required=True, description='Some array'),
})

# массив, который хранится в оперативной памяти
allarray = ['1']
name_space1 = api.namespace('list', description='list APIs')

# Парсер аргументов для генерации случайного массива
reqp = reqparse.RequestParser()
# добавление аргументов, передаваемых запросом GET
# например GET http://127.0.0.1:5000/list/makerand?len=7&minval=1&maxval=12
reqp.add_argument('len', type=int, required=False, default=10, help='Length of array')
reqp.add_argument('minval', type=float, required=False, default=0.0, help='Minimum value')
reqp.add_argument('maxval', type=float, required=False, default=1.0, help='Maximum value')

@name_space1.route("/makerand")
class MakeArrayClass(Resource):
    @name_space1.doc("")
    # ожидаем аргументы в запросе GET
    @name_space1.expect(reqp)
    # маршалинг данных в соответствии с моделью list_
    @name_space1.marshal_with(list_)
    def get(self):
        """Возвращение массива случайных значений от min до max"""
        args = reqp.parse_args()
        # Генерация массива случайных чисел
        array = [str(random() * (args['maxval'] - args['minval']) + args['minval'])
                for i in range(args['len'])]
        return {'len': str(args['len']), 'array': array}

@name_space1.route("/")
class ListClass(Resource):
    @name_space1.doc("")
    @name_space1.marshal_with(list_)
    def get(self):
        """Получение всего хранимого массива"""
        return {'len': str(len(allarray)), 'array': allarray}

    @name_space1.doc("")
    # ожидаем на входе данных в соответствии с моделью list_
    @name_space1.expect(list_)
    # маршалинг данных в соответствии с list_
    @name_space1.marshal_with(list_)
    def post(self):
        """Создание массива/наше описание функции пост"""
        global allarray
        # получить переданный массив из тела запроса
        allarray = api.payload['array']
        # возвратить новый созданный массив клиенту
        return {'len': str(len(allarray)), 'array': allarray}

# модель данные с двумя параметрами строкового типа
minmax = api.model('minmax', {
    'min': fields.String,
    'max': fields.String
}, required=True, description='two values')

# url 127.0.0.1/list/minmax
@name_space1.route("/minmax")
class MinMaxClass(Resource):
    @name_space1.doc("")
    # маршалинг данных в соответствии с моделью minmax
    @name_space1.marshal_with(minmax)
    def get(self):
        """Получение максимума и минимума массива"""
        global allarray
        return {'min': min(allarray), 'max': max(allarray)}

api.add_namespace(name_space1)

# подключение API из другого файла
from part.part import api as partns1
api.add_namespace(partns1)

from part.parttmpl import api as partns2
from part.parttmpl import templ as templ
api.add_namespace(partns2)
app.register_blueprint(templ, url_prefix='/templ')

if __name__ == '__main__':
    app.run(debug=True, port=5000)