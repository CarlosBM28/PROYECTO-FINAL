from flask import Flask, request, jsonify, render_template
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# =========================
# 🔹 CONEXIÓN POSTGRESQL
# =========================
def get_connection():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_CcM5qv8bToOj@ep-cold-surf-amdli41u-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"
    )

# =========================
# 🔹 CONEXIÓN MONGODB
# =========================
client = MongoClient("mongodb+srv://CarlosBM28:1234@cluster0.la7azje.mongodb.net/veterinaria?retryWrites=true&w=majority")
mongo_db = client["veterinaria"]
logs_collection = mongo_db["logs"]

# =========================
# 🔹 FUNCIÓN PARA GUARDAR LOGS
# =========================
def guardar_log(accion, producto_id):
    log = {
        "accion": accion,
        "producto_id": producto_id,
        "fecha": datetime.now()
    }
    logs_collection.insert_one(log)

# =========================
# 🔹 HOME
# =========================
@app.route('/')
def home():
    return render_template('index.html')

# =========================
# 🔹 OBTENER PRODUCTOS
# =========================
@app.route('/productos', methods=['GET'])
def obtener_productos():
    conexion = None
    cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM producto ORDER BY id DESC")
        datos = cursor.fetchall()

        return jsonify(datos)

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# =========================
# 🔹 CREAR PRODUCTO
# =========================
@app.route('/productos', methods=['POST'])
def crear_producto():
    conexion = None
    cursor = None
    try:
        data = request.json
        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO producto (nombre, tipo, precio, stock)
        VALUES (%s, %s, %s, %s) RETURNING id
        """

        cursor.execute(sql, (
            data['nombre'],
            data['tipo'],
            data['precio'],
            data['stock']
        ))

        producto_id = cursor.fetchone()[0]
        conexion.commit()

        guardar_log("Producto creado", producto_id)

        return jsonify({"mensaje": "Producto guardado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# =========================
# 🔹 ACTUALIZAR PRODUCTO
# =========================
@app.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    conexion = None
    cursor = None
    try:
        data = request.json
        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        UPDATE producto
        SET nombre=%s, tipo=%s, precio=%s, stock=%s
        WHERE id=%s
        """

        cursor.execute(sql, (
            data['nombre'],
            data['tipo'],
            data['precio'],
            data['stock'],
            id
        ))

        conexion.commit()
        guardar_log("Producto actualizado", id)

        return jsonify({"mensaje": "Producto actualizado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# =========================
# 🔹 ELIMINAR PRODUCTO
# =========================
@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conexion = None
    cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM producto WHERE id=%s", (id,))
        conexion.commit()

        guardar_log("Producto eliminado", id)

        return jsonify({"mensaje": "Producto eliminado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# =========================
# 🔹 OBTENER LOGS
# =========================
@app.route('/logs', methods=['GET'])
def obtener_logs():
    try:
        logs = list(logs_collection.find({}, {"_id": 0}))
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# 🔹 LOGS RECIENTES
# =========================
@app.route('/logs/recientes', methods=['GET'])
def logs_recientes():
    try:
        logs = list(
            logs_collection.find({}, {"_id": 0})
            .sort("fecha", -1)
            .limit(5)
        )
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# 🔹 ENDPOINT COMBINADO
# =========================
@app.route('/productos/<int:id>/detalle', methods=['GET'])
def detalle_producto(id):
    conexion = None
    cursor = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM producto WHERE id=%s", (id,))
        producto = cursor.fetchone()

        logs = list(
            logs_collection.find(
                {"producto_id": id},
                {"_id": 0}
            ).sort("fecha", -1).limit(10)
        )

        return jsonify({
            "producto": producto,
            "ultimas_actividades": logs
        })

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

# =========================
# 🔹 MAIN
# =========================
if __name__ == '__main__':
    try:
        conn = get_connection()
        print("✅ Conexión exitosa a PostgreSQL")
        conn.close()

        logs_collection.insert_one({"test": "conexion"})
        print("✅ Conexión exitosa a MongoDB")

    except Exception as e:
        print("❌ Error:", e)

    app.run(debug=True)

