import serial
import time

def testar_porta(porta):
    try:
        print(f"\nTestando porta {porta}...")
        esp32 = serial.Serial(porta, 115200, timeout=1)
        time.sleep(2)  # Aguarda inicialização
        
        print(f"Conectado em {porta}")
        print("Enviando comando de teste...")
        
        # Tenta enviar comando de LED
        esp32.write(b'2\n')
        esp32.flush()
        time.sleep(1)
        
        # Lê resposta
        while esp32.in_waiting:
            resposta = esp32.readline().decode('ascii', errors='ignore').strip()
            print(f"Resposta recebida: {resposta}")
        
        esp32.close()
        return True
        
    except Exception as e:
        print(f"Erro na porta {porta}: {str(e)}")
        return False

# Testa ambas as portas
portas = ['COM1', 'COM4']
for porta in portas:
    testar_porta(porta) 