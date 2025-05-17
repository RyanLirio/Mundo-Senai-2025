#define LED_PIN 2  // LED embutido do ESP32

// Estados do sistema
#define ESTADO_NORMAL 0
#define ESTADO_ALERTA 1
#define ESTADO_PERIGO 2

// Variáveis globais
int estado_atual = ESTADO_NORMAL;
bool piscando = false;
unsigned long tempo_ultimo_pisca = 0;
const int INTERVALO_PISCA = 100;  // Pisca mais rápido (100ms)

void pararPiscar() {
  piscando = false;
  estado_atual = ESTADO_NORMAL;
  digitalWrite(LED_PIN, LOW);
}

void iniciarPiscar() {
  estado_atual = ESTADO_PERIGO;
  piscando = true;
  tempo_ultimo_pisca = millis();
}

void setup() {
  // Inicia comunicação serial
  Serial.begin(115200);
  
  // Configura o LED
  pinMode(LED_PIN, OUTPUT);
  pararPiscar();  // Garante que começa desligado
  
  Serial.println("ESP32 Sistema de Alerta iniciado!");
}

void loop() {
  // Processa comandos seriais
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    switch (comando) {
      case '0':  // Estado normal
        pararPiscar();
        Serial.println("Estado: Normal");
        break;
        
      case '1':  // Estado de alerta
        estado_atual = ESTADO_ALERTA;
        piscando = false;
        digitalWrite(LED_PIN, HIGH);
        Serial.println("Estado: Alerta");
        break;
        
      case '2':  // Estado de perigo
        iniciarPiscar();
        Serial.println("Estado: Perigo!");
        break;
    }
  }

  // Controle do LED piscante
  if (piscando) {
    unsigned long tempo_atual = millis();
    if (tempo_atual - tempo_ultimo_pisca >= INTERVALO_PISCA) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));  // Inverte o estado do LED
      tempo_ultimo_pisca = tempo_atual;
    }
  }
}