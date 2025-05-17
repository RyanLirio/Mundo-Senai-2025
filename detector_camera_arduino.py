import cv2
import mediapipe as mp
import numpy as np
from ear_utils import calcular_ear
import serial
import time

# Estados do sistema
ESTADO_NORMAL = '0'
ESTADO_ALERTA = '1'
ESTADO_PERIGO = '2'

# Configuração do ESP32
try:
    arduino = serial.Serial('COM4', 115200, timeout=1)
    time.sleep(2)  # Aguarda a inicialização do ESP32
    print("ESP32 conectado com sucesso na porta COM4")
    
    # Teste inicial - testa todos os estados
    print("\nTestando comunicação...")
    print("Testando estado NORMAL...")
    arduino.write(ESTADO_NORMAL.encode())
    time.sleep(2)
    
    print("Testando estado ALERTA...")
    arduino.write(ESTADO_ALERTA.encode())
    time.sleep(2)
    
    print("Testando estado PERIGO...")
    arduino.write(ESTADO_PERIGO.encode())
    time.sleep(2)
    
    print("Voltando para estado NORMAL...")
    arduino.write(ESTADO_NORMAL.encode())
    time.sleep(1)
    
    # Lê e mostra qualquer resposta do ESP32
    while arduino.in_waiting:
        print("ESP32 diz:", arduino.readline().decode().strip())
        
except Exception as e:
    print(f"Erro ao conectar com ESP32: {e}")
    print("Verifique se:")
    print("1. O ESP32 está conectado na porta COM4")
    print("2. Nenhum outro programa está usando a porta")
    print("3. O dispositivo está instalado corretamente")
    arduino = None

EAR_LIMIAR = 0.12
tempo_olhos_fechados = 0
ultimo_estado = ESTADO_NORMAL
ultimo_tempo = time.time()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

olho_esquerdo_idx = [362, 385, 387, 263, 373, 380]
olho_direito_idx = [33, 160, 158, 133, 153, 144]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = face_mesh.process(rgb)

    if resultado.multi_face_landmarks:
        for face_landmarks in resultado.multi_face_landmarks:
            h, w, _ = frame.shape
            olho_esquerdo = []
            olho_direito = []

            for idx in olho_esquerdo_idx:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                olho_esquerdo.append((x, y))

            for idx in olho_direito_idx:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                olho_direito.append((x, y))

            for (x, y) in olho_esquerdo + olho_direito:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            ear_esquerdo = calcular_ear(olho_esquerdo)
            ear_direito = calcular_ear(olho_direito)
            ear_medio = (ear_esquerdo + ear_direito) / 2.0

            status = "Olhos Abertos" if ear_medio > EAR_LIMIAR else "Olhos Fechados"
            cor = (0, 255, 0) if status == "Olhos Abertos" else (0, 0, 255)
            cor = (0, 255, 255) if ear_medio > (EAR_LIMIAR - 0.03) and ear_medio < (EAR_LIMIAR + 0.03) else cor

            # Controle do LED baseado no tempo com os olhos fechados
            if arduino:
                tempo_atual = time.time()
                
                if ear_medio <= EAR_LIMIAR:
                    if ultimo_estado == ESTADO_NORMAL:
                        tempo_olhos_fechados = tempo_atual
                    
                    duracao_olhos_fechados = tempo_atual - tempo_olhos_fechados
                    
                    # Atualiza estado com base no tempo
                    if duracao_olhos_fechados >= 4.0 and ultimo_estado != ESTADO_PERIGO:
                        arduino.write(ESTADO_PERIGO.encode())
                        print("Enviando comando: PERIGO")
                        ultimo_estado = ESTADO_PERIGO
                    elif duracao_olhos_fechados >= 2.0 and ultimo_estado != ESTADO_ALERTA:
                        arduino.write(ESTADO_ALERTA.encode())
                        print("Enviando comando: ALERTA")
                        ultimo_estado = ESTADO_ALERTA
                else:
                    # Só envia comando se estiver mudando de estado
                    if ultimo_estado != ESTADO_NORMAL:
                        arduino.write(ESTADO_NORMAL.encode())
                        print("Enviando comando: NORMAL")
                        ultimo_estado = ESTADO_NORMAL
                        tempo_olhos_fechados = 0

                # Lê e mostra qualquer resposta do ESP32
                while arduino and arduino.in_waiting:
                    print("ESP32 diz:", arduino.readline().decode().strip())

            cv2.putText(frame, f"EAR: {ear_medio:.2f}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)
            cv2.putText(frame, status, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, cor, 2)

    cv2.imshow("Detecção de Olhos - EAR + MediaPipe", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close() 