from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import qrcode
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('acceso.db')
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------------
#  Inicializar DB con tablas
# -----------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')

    # Tabla de permisos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT NOT NULL,
            zona TEXT NOT NULL
        )
    ''')
    
    permisos = [
        ("Empleado", "A"),
        ("Empleado", "B"),
        ("Seguridad", "A"),
        ("Seguridad", "B"),
        ("Seguridad", "C"),
        ("Administrador", "A"),
        ("Administrador", "B"),
        ("Administrador", "C")
    ]

    # Insertar los datos automáticamente
    #cursor.executemany("INSERT INTO permisos (rol, zona) VALUES (?, ?)", permisos)
    # Eliminar datos de las tablas
    #cursor.execute("DELETE FROM permisos") 
    #cursor.execute("DELETE FROM permisos")
    #cursor.execute("DELETE FROM sqlite_sequence WHERE name='permisos'")

    conn.commit()
    conn.close()

# --- NUEVA RUTA: Panel de administración ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        rol = request.form['rol']

        # Insertar usuario
        cursor.execute("INSERT INTO usuarios (nombre, rol) VALUES (?, ?)", (nombre, rol))
        conn.commit()

        # Obtener el ID del nuevo usuario
        user_id = cursor.lastrowid

        # Generar el contenido del QR
        qr_data = f"ID:{user_id}|Nombre:{nombre}|Rol:{rol}"

        # Generar el QR y guardarlo en static/qr/
        qr_img = qrcode.make(qr_data)
        qr_path = os.path.join("static", "qr", f"user_{user_id}.png")
        qr_img.save(qr_path)

        return redirect(url_for('admin'))

    usuarios = cursor.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    return render_template('admin.html', usuarios=usuarios)


# -----------------------------
#  Ruta para registrar usuario en consola cmd
#  curl -X POST http://127.0.0.1:5000/registrar -H "Content-Type: application/json" -d "{\"nombre\":\"Juan perez\",\"rol\":\"Empleado\"}"
# -----------------------------
@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    data = request.json
    nombre = data['nombre']
    rol = data['rol']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, rol) VALUES (?, ?)", (nombre, rol))
    conn.commit()
    conn.close()

    return jsonify({"mensaje": f"Usuario {nombre} registrado con rol {rol}"}), 201

# -----------------------------
#  Ruta para validar acceso
# -----------------------------
@app.route('/validar', methods=['POST'])
def validar_acceso():
    data = request.json
    user_id = data['user_id']
    zona = data['zona']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener rol del usuario
    cursor.execute("SELECT rol FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    print(user)
    if user is None:
        return jsonify({"acceso": "denegado", "motivo": "Usuario no encontrado"}), 404

    rol = user['rol']
    # Revisar si el rol tiene permiso en la zona
    cursor.execute("SELECT * FROM permisos WHERE rol = ? AND zona = ?", (rol, zona))
    permiso = cursor.fetchone()
    print(rol,zona)
    conn.close()

    if permiso:
        return jsonify({"acceso": "permitido", "rol": rol, "zona": zona})
    else:
        return jsonify({"acceso": "denegado", "rol": rol, "zona": zona})

# Ruta para ver todos los usuarios
@app.route('/ver_usuarios', methods=['GET'])
def ver_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios')
    usuarios = cursor.fetchall()
    conn.close()

    # Convertir cada fila en diccionario
    resultado = [dict(usuario) for usuario in usuarios]
    return jsonify(resultado)

# Ruta para ver todos los permisos
@app.route('/ver_permisos', methods=['GET'])
def ver_permisos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM permisos')
    permisos = cursor.fetchall()
    conn.close()

    resultado = [dict(permiso) for permiso in permisos]
    return jsonify(resultado)


# -----------------------------
#  Iniciar backend
# -----------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
