import sqlite3
from flask import Flask
from flask import render_template, request, redirect, url_for, g
import os
from werkzeug import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './Archivos PDF'

DATABASE = "data.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def change_db(query,args=()):
    cur = get_db().execute(query, args)
    get_db().commit()
    cur.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    prestadores_servicio=query_db("SELECT * FROM prestador")
    return render_template("index.html",prestadores_servicio=prestadores_servicio)

@app.route('/carga')
def upload_file():
        # renderiamos la plantilla "formulario.html"
        return render_template('archivo.html')

@app.route('/create', methods=['GET', 'POST'])
def create():

    if request.method == "GET":
        return render_template("create.html",prestador=None)

    if request.method == "POST":
        prestador=request.form.to_dict()
        values=[prestador["nombre"],prestador["telefono"],prestador["email"],prestador["direccion"],prestador["edad"],prestador["experiencia"],prestador["especialidad"]]
        change_db("INSERT INTO prestador (nombre,telefono,email,direccion,edad,experiencia,especialidad) VALUES (?,?,?,?,?,?,?)",values)
        return redirect(url_for("index"))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def udpate(id):

    if request.method == "GET":
        prestador=query_db("SELECT * FROM prestador WHERE id=?",[id],one=True)
        return render_template("update.html",prestador=prestador)

    if request.method == "POST":
        prestador=request.form.to_dict()
        values=[prestador["nombre"],prestador["telefono"],prestador["email"],prestador["direccion"],prestador["edad"],prestador["experiencia"],prestador["especialidad"],id]
        change_db("UPDATE prestador SET nombre=?, telefono=?, email=?, direccion=?, edad=?, experiencia=?, especialidad=? WHERE ID=?",values)
        return redirect(url_for("index"))

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):

    if request.method == "GET":
        prestador=query_db("SELECT * FROM prestador WHERE id=?",[id],one=True)
        return render_template("delete.html",prestador=prestador)

    if request.method == "POST":
        change_db("DELETE FROM prestador WHERE id = ?",[id])
        return redirect(url_for("index"))


@app.route("/upload", methods=['POST'])
def uploader():
 if request.method == 'POST':
  # obtenemos el archivo del input "archivo"
  f = request.files['archivo']
  filename = secure_filename(f.filename)
  # Guardamos el archivo en el directorio "Archivos PDF"
  f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
  # Retornamos una respuesta satisfactoria
  return "<h1>Archivo subido exitosamente</h1>"

if __name__ == '__main__':
 # Iniciamos la aplicación
 app.run(debug=True)