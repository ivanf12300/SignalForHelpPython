import cv2
import mediapipe as mp
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_draw
import playsound3
import threading 

reproducir = False
firstFrame = True
AlreadyReproduced = False 

audio_en_reproduccion = False 

def reproducirAudio(sound):
    global audio_en_reproduccion
    playsound3.playsound(sound)
    audio_en_reproduccion = False

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
        totalDeFrames += 1
        break

    frame = cv2.flip(frame, 1)
    results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    dedos_levantados = 0

    if results.multi_hand_landmarks: # type: ignore
        for index, hand_landmarks in enumerate(results.multi_hand_landmarks): # type: ignore
            # Dibujar lineas de la mano
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS # type: ignore
            )

            puntos = hand_landmarks.landmark
            tips = [4, 8, 12, 16, 20]

            hand_label = results.multi_handedness[index].classification[0].label #type: ignore

            if hand_label == "Right":
                if puntos[tips[0]].x < puntos[tips[0] - 1].x:
                    dedos_levantados += 1
            else: 
                if puntos[tips[0]].x > puntos[tips[0] - 1].x:
                    dedos_levantados += 1
            
            # Otros dedos
            for tip in tips[1:]:
                if puntos[tip].y < puntos[tip - 2].y:
                    dedos_levantados += 1

            if totalDeFrames == framesEsperando and ciclos >= 0:
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
                frames_alerta = 490

            # Mostrar información en pantalla

            if not alerta_activa:
                cv2.putText(frame, f"Dedos: {dedos_levantados}", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Ciclos: {ciclos}/5", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                totalDeFrames += 1
            else:
                continue

    if reproducir and not audio_en_reproduccion:
        audio_en_reproduccion = True
        reproducir = False
        t = threading.Thread(
        target=reproducirAudio,
        args=("Detector de signal for help/alarm1.mp3",),
        daemon=True)
        t.start()

    if alerta_activa:
        totalDeFrames = 0
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255),cv2.BORDER_TRANSPARENT)
        cv2.putText(
            frame,
            "alguien necesita ayuda",
            (40,240),
            cv2.FONT_HERSHEY_DUPLEX,
            1.5,
            (0, 0, 0),
            4
        )
        frames_alerta -= 1
        reproducir = True

        if frames_alerta <= 0:
            alerta_activa = False
            reproducir = False

        # print(f"Current frame: {frames_alerta}, Has been reproduced: {AlreadyReproduced}")

    cv2.imshow("Detector de Signal For Help", frame)

    # Salir con ESC
    key = cv2.waitKey(1)
    if key == 27:
        break

camara.release()
cv2.destroyAllWindows()
