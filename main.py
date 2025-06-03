# main.py
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os  # Importa el módulo os

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'  # Reemplaza con una clave secreta segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'  # Reemplaza con tu URI de base de datos
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactiva el seguimiento de modificaciones
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define la carpeta para guardar los archivos subidos

# Inicialización de SQLAlchemy
db = SQLAlchemy(app)

# Crea la carpeta de subidas si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Definición del modelo de la base de datos
class MiTabla(db.Model):  # Reemplaza "MiTabla" con el nombre de tu tabla
    id = db.Column(db.Integer, primary_key=True)
    columna1 = db.Column(db.String(255))  # Reemplaza con tus columnas
    columna2 = db.Column(db.Integer)
    # ... agrega más columnas según tu archivo Excel ...

    def __repr__(self):
        return f"<MiTabla(columna1='{self.columna1}', columna2={self.columna2})>"

# Crea las tablas de la base de datos
with app.app_context():
    db.create_all()

# Ruta para mostrar el formulario de carga
@app.route('/')
def upload():
    return render_template('upload-excel.html')

# Ruta para procesar el archivo subido
@app.route('/view', methods=['POST'])
def view():
    if request.method == 'POST':
        # Verifica si se envió un archivo
        if 'file' not in request.files:
            return "No file part"  # Deberías usar flash messages en una aplicación real

        file = request.files['file']

        # Si el usuario no selecciona un archivo, el navegador envía una cadena vacía
        if file.filename == '':
            return "No selected file"  # Deberías usar flash messages en una aplicación real

        # Guarda el archivo en la carpeta de subidas
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            # Lee el archivo Excel con Pandas
            data = pd.read_excel(filepath)

            # Itera sobre las filas del DataFrame y guarda los datos en la base de datos
            for index, row in data.iterrows():
                registro = MiTabla(
                    columna1=str(row['nombre']),  # Asegúrate de que los nombres de las columnas coincidan
                    columna2=int(row['edad'])
                    # ... asigna los valores de las otras columnas ...
                )
                db.session.add(registro)
            db.session.commit()

            # Elimina el archivo subido después de procesarlo
            os.remove(filepath)

            return "Datos guardados correctamente en la base de datos"  # Deberías usar render_template y mostrar una página de éxito

        except Exception as e:
            db.session.rollback()  # Revierte la transacción en caso de error
            os.remove(filepath)  # Elimina el archivo subido
            return f"Error al procesar el archivo: {str(e)}"  # Deberías usar flash messages y mostrar una página de error

# Main Driver Function
if __name__ == '__main__':
    # Run the application on the local development server
    app.run(debug=True)