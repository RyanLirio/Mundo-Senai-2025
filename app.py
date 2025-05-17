from flask import Flask, render_template, Response, jsonify
import cv2
from detector_sonolencia_motorista import DetectorSonolencia
import threading
import time
import logging
import os

# Configuração de logging mais limpa
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Desabilita logs do Flask
logging.getLogger('werkzeug').disabled = True

app = Flask(__name__)
app.logger.disabled = True

# Variáveis globais para compartilhar estado
estado_atual = {
    'status': 'Normal',
    'blink_count': 0,
    'eyes_closed_time': 0,
    'static_eyes_time': 0,
    'ear_value': 0.3  # Valor inicial do EAR
}

# Inicializa o detector
detector = DetectorSonolencia()
camera = cv2.VideoCapture(0)

def gerar_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Processa o frame com o detector
            frame_processado = detector.processar_frame(frame)
            
            # Atualiza estado global
            global estado_atual
            ear_medio = 0.3  # Valor padrão
            if hasattr(detector, 'historico_ear') and len(detector.historico_ear) > 0:
                ear_medio = float(detector.historico_ear[-1])  # Pega o último valor do EAR
            
            estado_atual.update({
                'status': 'Normal' if detector.nivel_alerta == 0 else 'Atenção' if detector.nivel_alerta == 1 else 'Perigo',
                'blink_count': len(detector.historico_piscadas),
                'eyes_closed_time': round(detector.tempo_olhos_fechados, 1),
                'static_eyes_time': round(detector.tempo_olhos_estaticos, 1),
                'ear_value': round(ear_medio, 3)
            })
            
            # Converte o frame para JPEG
            ret, buffer = cv2.imencode('.jpg', frame_processado)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gerar_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    return jsonify(estado_atual)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def cleanup():
    print("Limpando recursos...")
    camera.release()
    detector.finalizar()

if __name__ == '__main__':
    try:
        clear_terminal()
        print("\n=== Sistema de Detecção de Sonolência ===")
        print("✨ Iniciando servidor web...")
        print("\n🌐 Acesse o sistema em:")
        print("   http://localhost:5000")
        print("\n⚡ Pressione Ctrl+C para encerrar\n")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário")
    finally:
        cleanup() 