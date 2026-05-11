from flask import Flask, request, jsonify, render_template
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import functools

app = Flask(__name__)
app.config['SECRET_KEY'] = 'veterinaria_super_secret_key_2026_proyecto_final_seguro_123'


# =========================
# CONEXIÓN POSTGRESQL
# =========================
def get_connection():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_CcM5qv8bToOj@ep-cold-surf-amdli41u-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )


# =========================
# CONEXIÓN MONGODB
# =========================
client = MongoClient("mongodb+srv://CarlosBM28:1234@cluster0.la7azje.mongodb.net/veterinaria?retryWrites=true&w=majority")
mongo_db = client["veterinaria"]

logs_collection = mongo_db["logs"]
users_collection = mongo_db["users"]


# =========================
# GUARDAR LOGS
# =========================
def guardar_log(accion, producto_id, usuario=None):
    logs_collection.insert_one({
        "accion": accion,
        "producto_id": producto_id,
        "usuario": usuario,
        "fecha": datetime.now()
    })


# =========================
# JWT DECORADORES
# =========================
def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token requerido"}), 401

        try:
            if token.startswith("Bearer "):
                token = token[7:]

            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

            request.current_user = data

        except Exception:
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Token requerido"}), 401

        try:
            if token.startswith("Bearer "):
                token = token[7:]

            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

            if data.get("rol") != "admin":
                return jsonify({"error": "Acceso denegado"}), 403

            request.current_user = data

        except Exception:
            return jsonify({"error": "Token inválido"}), 401

        return f(*args, **kwargs)

    return decorated


# =========================
# RUTAS FRONT
# =========================
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index.html')


# =========================
# REGISTRO
# =========================
@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.json

        nombre = data['nombre']
        email = data['email'].lower()
        password = data['password']
        rol = data.get('rol', 'cliente')

        if users_collection.find_one({"email": email}):
            return jsonify({"error": "Usuario ya existe"}), 400

        hashed = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

        users_collection.insert_one({
            "nombre": nombre,
            "email": email,
            "password": hashed,
            "rol": rol,
            "fecha_registro": datetime.now().strftime("%d/%m/%Y %H:%M")
        })

        return jsonify({"mensaje": "Usuario registrado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# LOGIN
# =========================
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.json

        email = data['email'].lower()
        password = data['password']

        user = users_collection.find_one({"email": email})

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 401

        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password']
        ):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        token = jwt.encode({
            "nombre": user['nombre'],
            "email": user['email'],
            "rol": user['rol'],
            "exp": datetime.now(timezone.utc) + timedelta(hours=8)
        },
        app.config['SECRET_KEY'],
        algorithm="HS256")

        return jsonify({
            "mensaje": "Login exitoso",
            "token": token,
            "rol": user['rol'],
            "nombre": user['nombre']
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# PERFIL
# =========================
@app.route('/auth/me')
@token_required
def perfil():
    return jsonify(request.current_user)


# =========================
# OBTENER PRODUCTOS
# =========================
@app.route('/productos')
@token_required
def obtener_productos():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM producto ORDER BY id DESC")
        productos = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(productos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# CREAR PRODUCTO
# =========================
@app.route('/productos', methods=['POST'])
@admin_required
def crear_producto():
    try:
        data = request.json

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO producto (nombre, tipo, precio, stock)
            VALUES (%s,%s,%s,%s)
            RETURNING id
        """, (
            data['nombre'],
            data['tipo'],
            data['precio'],
            data['stock']
        ))

        producto_id = cursor.fetchone()[0]

        conn.commit()

        guardar_log(
            "Producto creado",
            producto_id,
            request.current_user['nombre']
        )

        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Producto creado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ACTUALIZAR PRODUCTO
# =========================
@app.route('/productos/<int:id>', methods=['PUT'])
@admin_required
def actualizar_producto(id):
    try:
        data = request.json

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE producto
            SET nombre=%s, tipo=%s, precio=%s, stock=%s
            WHERE id=%s
        """, (
            data['nombre'],
            data['tipo'],
            data['precio'],
            data['stock'],
            id
        ))

        conn.commit()

        guardar_log(
            "Producto actualizado",
            id,
            request.current_user['nombre']
        )

        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Producto actualizado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# ELIMINAR PRODUCTO
# =========================
@app.route('/productos/<int:id>', methods=['DELETE'])
@admin_required
def eliminar_producto(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM producto WHERE id=%s",
            (id,)
        )

        conn.commit()

        guardar_log(
            "Producto eliminado",
            id,
            request.current_user['nombre']
        )

        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Producto eliminado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# LOGS
# =========================
@app.route('/logs')
@admin_required
def obtener_logs():
    try:
        logs = list(
            logs_collection.find({}, {"_id": 0}).sort("fecha", -1)
        )

        for log in logs:
            if isinstance(log["fecha"], datetime):
                log["fecha"] = log["fecha"].strftime("%d/%m/%Y %H:%M")

        return jsonify(logs)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/logs/recientes')
@admin_required
def logs_recientes():
    try:
        logs = list(
            logs_collection.find({}, {"_id": 0})
            .sort("fecha", -1)
            .limit(5)
        )

        for log in logs:
            if isinstance(log["fecha"], datetime):
                log["fecha"] = log["fecha"].strftime("%d/%m/%Y %H:%M")

        return jsonify(logs)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# USUARIOS
# =========================
@app.route('/usuarios')
@admin_required
def listar_usuarios():
    try:
        usuarios = list(
            users_collection.find({}, {"_id": 0, "password": 0})
        )

        return jsonify(usuarios)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    try:
        conn = get_connection()
        print("✅ PostgreSQL conectado")
        conn.close()

        logs_collection.insert_one({"test": "conexion"})
        print("✅ MongoDB conectado")

    except Exception as e:
        print("❌ Error:", e)

    app.run(debug=True, use_reloader=False)
