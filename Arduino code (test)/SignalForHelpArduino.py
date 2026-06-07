import cv2
import mediapipe as mp
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_draw
#import playsound3
import serial
import time

# La alarma debe estar conectada en el puerto 13

puerto_arduino = serial.Serial("COM3",9600)
time.sleep(2)

reproducir = False

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7
)
camara = cv2.VideoCapture(0)

estado = 4
ciclos = 0
alerta_activa = False
frames_alerta = 0

framesEsperando = 100
totalDeFrames = 0

while True:
    success, frame = camara.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    dedos_levantados = 0

    if results.multi_hand_landmarks: # type: ignore
        for hand_landmarks in results.multi_hand_landmarks: # type: ignore
            # Dibujar lineas de la mano
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS # type: ignore
            )

            puntos = hand_landmarks.landmark
            tips = [4, 8, 12, 16, 20]

            # Pulgar
            if puntos[tips[0]].x < puntos[tips[0] - 1].x:
                dedos_levantados += 1

            # Otros dedos
            for tip in tips[1:]:
                if puntos[tip].y < puntos[tip - 2].y:
                    dedos_levantados += 1

            if totalDeFrames == framesEsperando and ciclos >= 1:
                totalDeFrames = 0 
                ciclos = 0

            # Estados para la señal de ayuda
            if estado == 4 and dedos_levantados == 4:
                estado = 0
            
            elif estado == 0 and dedos_levantados == 0:
                estado = 4
                ciclos += 1

            if ciclos >= 5:
                alerta_activa = True
                ciclos = 0  
                frames_alerta = 90   

            # Mostrar información en pantalla
            cv2.putText(frame, f"Dedos: {dedos_levantados}", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Ciclos: {ciclos}/5", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            totalDeFrames += 1

            if reproducir == True:
                puerto_arduino.write(b"1")
                #playsound3.playsound("alarm1.mp3")
            else:
                continue

    if alerta_activa:
        totalDeFrames = 0
        cv2.rectangle(frame,(0,0),(1000,1000),(0,0,255),cv2.FILLED)
        cv2.putText(
            frame,
            "alguien necesita ayuda",
            (50, 220),
            cv2.FONT_ITALIC,
            1.5,
            (0, 0, 0),
            4
        )
        reproducir = True
        frames_alerta -= 1
        if frames_alerta <= 0:
            puerto_arduino.write(b"0")
            alerta_activa = False
            reproducir = False

    cv2.imshow("Detector de Signal For Help", frame)

    # Salir con ESC
    key = cv2.waitKey(1)
    if key == 27:
        break

camara.release()
cv2.destroyAllWindows()