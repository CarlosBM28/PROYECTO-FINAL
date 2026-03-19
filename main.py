from flask import Flask, request, jsonify, render_template
import psycopg2
import psycopg2.extras

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="veterinaria",
        user="postgres",
        password="1234"
    )

@app.route('/')
def home():
    return render_template('index.html')

# =========================
# 🔹 OBTENER PRODUCTOS
# =========================
@app.route('/productos', methods=['GET'])
def obtener_productos():
    try:
        conexion = get_connection()
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM producto ORDER BY id DESC")
        datos = cursor.fetchall()

        return jsonify(datos)

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        conexion.close()

# =========================
# 🔹 CREAR PRODUCTO
# =========================
@app.route('/productos', methods=['POST'])
def crear_producto():
    try:
        data = request.json
        conexion = get_connection()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO producto (nombre, tipo, precio, stock)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql, (
            data['nombre'],
            data['tipo'],
            data['precio'],
            data['stock']
        ))

        conexion.commit()

        return jsonify({"mensaje": "Producto guardado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        conexion.close()

# =========================
# 🔹 ACTUALIZAR PRODUCTO
# =========================
@app.route('/productos/<int:id>', methods=['PUT'])
def actualizar_producto(id):
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

        return jsonify({"mensaje": "Producto actualizado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        conexion.close()

# =========================
# 🔹 ELIMINAR PRODUCTO
# =========================
@app.route('/productos/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM producto WHERE id=%s", (id,))
        conexion.commit()

        return jsonify({"mensaje": "Producto eliminado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        cursor.close()
        conexion.close()

if __name__ == '__main__':
    try:
        conn = get_connection()
        print("✅ Conexión exitosa a PostgreSQL")
        conn.close()
    except Exception as e:
        print("❌ Error de conexión:", e)

    app.run(debug=True)