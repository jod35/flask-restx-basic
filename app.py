from flask import Flask,request
from flask_restx import Api,Resource,fields
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

basedir=os.path.dirname(os.path.realpath(__file__))


app=Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///' +os.path.join(basedir,'api.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False


db=SQLAlchemy(app)
api=Api(app)


#serialize the data
model=api.model(
    'Model'
    ,{  "id":fields.Integer,
        "name":fields.String,
        "desc":fields.String,
        "date":fields.DateTime(dt_format='rfc822')
    }
)




class Todo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.Text())
    desc=db.Column(db.Text())
    date=db.Column(db.DateTime(),default=datetime.utcnow)


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()




@api.route('/hello')
class Hello(Resource):
    def get(self):
        return {"message":"Hello World"}

@api.route('/todos')
class Todos(Resource):

    @api.marshal_with(model,envelope='todos')
    def get(self):
        todos=Todo.query.all()
        return todos

    @api.marshal_with(model,envelope='todo')
    def post(self):
        data=request.get_json()

        new_todo=Todo(name=data.get('name'),desc=data.get('desc'))

        new_todo.save()

        return new_todo


@api.route('/todo/<int:id>')
class Todo2(Resource):

    @api.marshal_with(model,envelope='todo')
    def put(self,id):
        todo=Todo.query.get_or_404(id)

        data=request.get_json()

        todo.name=data.get('name')

        todo.desc=data.get('desc')
        
        db.session.commit()

        return todo


    @api.marshal_with(model,envelope='todo')
    def get(self,id): 
        todo=Todo.query.get_or_404(id)

        return todo

    @api.marshal_with(model,envelope='todo')
    def delete(self,id):
        todo=Todo.query.get_or_404(id)

        todo.delete()

        return todo




@app.shell_context_processor
def make_shell_context():
    return {
        'app':app,
        'api':api,
        'db':db,
        'Todo':Todo
    }



if __name__ == "__main__":
    app.run(debug=True)

