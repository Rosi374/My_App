from app import app, db
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory

# Carpeta de subida de avatares
UPLOAD_FOLDER = 'app/static/uploads'

# Crear la carpeta "uploads" si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Función para verificar la extensión de archivo permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}
@app.route('/avatar/<filename>')
def avatar(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Verifica si se ha enviado un archivo
        if 'avatar' not in request.files:
            flash('No se ha seleccionado un archivo de avatar.')
            return redirect(request.url)

        avatar = request.files['avatar']

        # Verifica si el archivo tiene un nombre válido y una extensión permitida
        if avatar.filename == '':
            flash('No se ha seleccionado un archivo de avatar.')
            return redirect(request.url)
        
        if not allowed_file(avatar.filename):
            flash('El formato de archivo no está permitido. Utilice archivos jpg, jpeg, png o gif.')
            return redirect(request.url)

        # Genera un nombre de archivo seguro para el avatar
        filename = secure_filename(avatar.filename)
        avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Guarda el archivo de avatar en el servidor
        avatar.save(avatar_path)

        cursor = db.cursor()

        # Verifica si el usuario ya existe en la base de datos
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('El nombre de usuario ya está en uso. Por favor, elige otro.')
            return redirect(url_for('registro'))

        # Inserta un nuevo usuario en la base de datos
        insert_query = "INSERT INTO usuarios (username, email, password, avatar) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (username, email, password, avatar_path))
        db.commit()

        flash('¡Registro exitoso! Ahora puedes iniciar sesión.')
        return redirect(url_for('index'))

    return render_template('registro.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()

        # Verifica si el usuario existe en la base de datos
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            stored_password = user[2]  # Supongamos que la contraseña se almacena en la tercera columna de la tabla
            if password == stored_password:
                flash('¡Inicio de sesión exitoso!', 'success')
                session['username'] = username  # Establece la sesión del usuario
                return redirect(url_for('principal'))  # Redirige a la página principal
            else:
                flash('Contraseña incorrecta. Inténtalo de nuevo.', 'error')
        else:
            flash('Usuario no encontrado. Regístrate si eres nuevo.', 'error')

    # Si hay errores o si no se envió un formulario POST, redirige a la página de inicio de sesión
    return redirect(url_for('index'))

@app.route('/upload/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/principal')
def principal():
    # Verifica si el usuario está autenticado antes de mostrar la página principal
    if 'username' in session:
        # Obtén el nombre de usuario de la sesión
        username = session['username']

        cursor = db.cursor()
        
        # Consulta la base de datos para obtener la información del usuario
        cursor.execute("SELECT username, avatar FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            # Crea un diccionario con los datos del usuario
            user_data = {
                'username': user[0],
                'avatar': os.path.basename(user[1])  # Nombre del archivo del avatar
            }

            return render_template('principal.html', user=user_data)
        else:
            flash('Usuario no encontrado. Regístrate si eres nuevo.', 'error')
    else:
        flash('Debes iniciar sesión primero.', 'error')
        return redirect(url_for('index'))
    
@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'username' in session:
        if request.method == 'POST':
            # Obtén los datos del formulario
            new_username = request.form['new_username']
            new_email = request.form['new_email']
            new_password = request.form['new_password']

            # Verifica si se ha enviado un nuevo archivo de avatar
            if 'new_avatar' in request.files:
                new_avatar = request.files['new_avatar']

                # Verifica si el archivo tiene un nombre válido y una extensión permitida
                if new_avatar.filename != '' and allowed_file(new_avatar.filename):
                    # Genera un nombre de archivo seguro para el nuevo avatar
                    filename = secure_filename(new_avatar.filename)
                    avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                    # Guarda el nuevo avatar en el servidor
                    new_avatar.save(avatar_path)

                    # Actualiza la ruta del avatar en la base de datos
                    cursor = db.cursor()
                    update_query = "UPDATE usuarios SET username = %s, email = %s, password = %s, avatar = %s WHERE username = %s"
                    cursor.execute(update_query, (new_username, new_email, new_password, avatar_path, session['username']))
                    db.commit()
                else:
                    flash('El formato de archivo no está permitido. Utilice archivos jpg, jpeg, png o gif.', 'error')
                    return redirect(url_for('editar_perfil'))

            else:
                # Si no se cargó un nuevo avatar, actualiza los otros datos del perfil
                cursor = db.cursor()
                update_query = "UPDATE usuarios SET username = %s, email = %s, password = %s WHERE username = %s"
                cursor.execute(update_query, (new_username, new_email, new_password, session['username']))
                db.commit()

            flash('Los cambios en tu perfil se han guardado correctamente.', 'success')

            # Actualiza la sesión del usuario si cambió el nombre de usuario
            if new_username != session['username']:
                session['username'] = new_username

        return render_template('editar_perfil.html')
    else:
        flash('Debes iniciar sesión primero.', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Cierra la sesión del usuario
    session.pop('username', None)
    flash('Sesión cerrada con éxito.', 'success')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)