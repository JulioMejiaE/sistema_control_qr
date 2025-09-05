import cv2
from pyzbar.pyzbar import decode
import sqlite3

# Configuración de zonas por rol (ejemplo simple)
PERMISOS = {
    "Administrador": ["A", "B", "C"],
    "Empleado": ["A"],
    "Visitante": ["B"]
}

def get_usuario(user_id):
    conn = sqlite3.connect("acceso.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, rol FROM usuarios WHERE id = ?", (user_id,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario

def validar_acceso(usuario, zona):
    if usuario:
        rol = usuario[2]  # columna rol
        if zona in PERMISOS.get(rol, []):
            return f"✅ Acceso permitido a {zona} para {usuario[1]} ({rol})", (0, 255, 0)
        else:
            return f"❌ Acceso denegado a {zona} para {usuario[1]} ({rol})", (0, 0, 255)
    else:
        return "⚠️ Usuario no encontrado en DB", (0, 0, 255)

def main():
    cap = cv2.VideoCapture(0)  # Cámara 0
    zona = "A"  # Cambia según lo que quieras probar

    print("📷 Lector QR con validación. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        codes = decode(frame)

        for code in codes:
            data = code.data.decode('utf-8')

            try:
                partes = dict(item.split(":") for item in data.split("|"))
                user_id = int(partes["ID"])
            except:
                msg, color = ("⚠️ Error al leer QR", (0, 0, 255))
                user_id = None

            if user_id:
                usuario = get_usuario(user_id)
                msg, color = validar_acceso(usuario, zona)

            # Dibujar rectángulo y mensaje
            (x, y, w, h) = code.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, msg, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, color, 2)

        cv2.imshow("Lector QR DB", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
