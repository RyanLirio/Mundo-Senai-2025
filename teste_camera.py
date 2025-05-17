import cv2

def testar_cameras():
    # Tenta acessar diferentes índices de câmera
    for i in range(4):  # Testa câmeras de 0 a 3
        print(f"\nTentando acessar câmera {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Câmera {i} está funcionando!")
                print(f"   Resolução: {frame.shape[1]}x{frame.shape[0]}")
                cap.release()
            else:
                print(f"❌ Câmera {i} não retornou imagem")
        else:
            print(f"❌ Não foi possível acessar a câmera {i}")
        
        cap.release()

if __name__ == "__main__":
    print("=== Teste de Câmeras ===")
    testar_cameras()
    print("\nTeste concluído!") 