# 🐾 Proyecto Veterinaria

Sistema web para la gestión de una clínica veterinaria.

---

## 📦 Requisitos

- Python 3.10 o superior
- Git
- Entorno virtual (venv)

---

## 🚀 Instalación y ejecución local

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/CarlosBM28/PROYECTO-FINAL.git
cd PROYECTO-FINAL
---

### 2️⃣ Crear entorno virtual

```bash
python -m venv venv

-----------------------------------------------------

## ENTREGA CORTE 2 PASO A PASO README ##

# 🐾 Proyecto Final - Integración SQL y NoSQL (Flask)

## 📌 Descripción

Este proyecto consiste en el desarrollo de una aplicación web utilizando **Flask**, que implementa una arquitectura de **persistencia políglota**, integrando:

* **PostgreSQL (Neon)** → para datos estructurados (productos)
* **MongoDB Atlas** → para datos no estructurados (logs de actividad)

El objetivo es demostrar la capacidad de manejar distintos tipos de datos y combinarlos en una misma aplicación.

---

## 🧠 Justificación del uso de NoSQL

Se utilizó MongoDB para almacenar logs debido a que:

* Son datos dinámicos
* No requieren una estructura rígida
* Pueden crecer rápidamente
* No necesitan relaciones complejas

Esto permite mayor flexibilidad frente a bases de datos relacionales.

---

## ⚙️ Tecnologías utilizadas

* Python
* Flask
* PostgreSQL (Neon - nube)
* MongoDB Atlas
* Postman (pruebas)
* psycopg2
* pymongo

---

## 🗂️ Estructura del proyecto

```
PROYECTO FINAL/
│
├── main.py
├── templates/
│   └── index.html
├── venv/
└── README.md
```

---

## 🔌 Configuración

### 1. Clonar repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd PROYECTO FINAL
```

---

### 2. Activar entorno virtual

```bash
venv\Scripts\Activate
```

---

### 3. Instalar dependencias

```bash
pip install flask psycopg2 pymongo
```

---

## 🛢️ Configuración de bases de datos

### 🔹 PostgreSQL (Neon)

Se utiliza una base de datos en la nube con la siguiente estructura:

```sql
CREATE TABLE producto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    tipo VARCHAR(100),
    precio INTEGER,
    stock INTEGER
);
```

---

### 🔹 MongoDB Atlas

Se utiliza para almacenar logs en la colección:

```
logs
```

Ejemplo de documento:

```json
{
  "accion": "Producto creado",
  "producto_id": 1,
  "fecha": "2026-04-14"
}
```

---

## 🚀 Ejecución del proyecto

```bash
python main.py
```

El servidor correrá en:

```
http://127.0.0.1:5000
```

---

## 🔗 Endpoints

### 🔹 Crear producto

```
POST /productos
```

Body:

```json
{
  "nombre": "Antipulgas",
  "tipo": "Medicamento",
  "precio": 20000,
  "stock": 10
}
```

---

### 🔹 Obtener productos

```
GET /productos
```

---

### 🔹 Obtener logs (MongoDB)

```
GET /logs
```

---

### 🔹 Endpoint combinado ⭐

```
GET /productos/<id>/detalle
```

Retorna:

* Información del producto (PostgreSQL)
* Últimas actividades (MongoDB)

---

## 🧪 Pruebas

Las pruebas fueron realizadas con **Postman**, verificando:

* Creación de productos
* Consulta de datos SQL
* Consulta de logs NoSQL
* Integración entre ambas bases de datos

---

## 📸 Evidencias

Se incluyen capturas de:

* POST /productos
* GET /productos
* GET /logs
* GET /productos/{id}/detalle

---

## 🎯 Conclusión

Se logró implementar una solución de persistencia políglota, combinando bases de datos relacionales y no relacionales, permitiendo manejar distintos tipos de información de manera eficiente y escalable.

---

## 👩‍💻 Autora

Laura Valentina

