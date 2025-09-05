import cv2
from pyzbar.pyzbar import decode

def main():
    # Abrir la cámara
    cap = cv2.VideoCapture(0)

    print("📷 Lector QR iniciado. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar códigos QR en la imagen
        codes = decode(frame)

        for code in codes:
            data = code.data.decode('utf-8')
            print(f"🔹 QR detectado: {data}")

            # Dibujar un rectángulo en el QR
            (x, y, w, h) = code.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 255, 0), 2)

        # Mostrar la cámara
        cv2.imshow("Lector QR", frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
