class JanelaSecundaria(QMainWindow):
    def __init__(self, file_path, x, y, tipo_arquivo, janela_principal):
        super().__init__()  # Inicializa a classe base QMainWindow
        self.setWindowTitle("Manipulação de Imagens e Vídeos")  # Define o título da janela
        self.setGeometry(100, 100, 1000, 800)  # Define a posição e o tamanho da janela
        self.tipo_arquivo = tipo_arquivo  # Armazena o tipo de arquivo
        self.video_capture = None  # Variável para captura de vídeo (inicialmente None)
        self.timer = QTimer()  # Cria um timer para atualizações periódicas
        self.janela_principal = janela_principal  # Armazena referência para a janela principal
        self.original_image = None  # Armazena a imagem original
        self.cropped_image = None  # Armazena a imagem cortada
        self.zoom_level = 1.0  # Nível de zoom inicial
        self.rect_inicio_ponto = None  # Ponto inicial do retângulo de seleção
        self.rect_fim_ponto = None  # Ponto final do retângulo de seleção
        self.roi_coords = []  # Coordenadas da região de interesse (ROI)
        self.imagem_convolucao = None  # Armazena a imagem filtrada
        self.imagem_bin_cinza_cores = None  # Armazena a imagem binária/cinza/cores
        self.imagem_antes_filtro = None  # Armazena a imagem antes de aplicar o filtro
        self.velocidade_reproducao = 1.0  # Velocidade de reprodução padrão
        self.invertido = False  # Indica se o vídeo está invertido
        self.pontos_de_corte = []  # Lista de pontos de corte no vídeo
        self.operacao_cascata = False  # Indica se operações em cascata estão ativadas
        self.frame_index = 0  # Índice do quadro atual
        self.frames = []  # Lista de quadros do vídeo
        self.cont = 1  # Variável de contagem
        self.i = 0  # Variável auxiliar
        self.f = 0  # Variável auxiliar
        self.op = ""  # Variável para operação
        self.timer = QTimer()  # Cria um timer para atualizações periódicas (duplicado)
        self.aplicar_filtro_video = False  # Controle para aplicar filtro durante reprodução de vídeo
        self._setup_ui(file_path, x, y)  # Chama o método para configurar a interface do usuário
        self.showMaximized()  # Maximiza a janela

        self.timer.timeout.connect(self.atualizar_quadro)  # Conecta o timer ao método de atualização de quadros
        self.timer.start(int(1000 / (self.velocidade_reproducao * 30)))  # Inicia o timer com intervalo baseado na velocidade de reprodução

    def _setup_ui(self, file_path, x, y):
        main_layout = QVBoxLayout()  # Cria um layout vertical principal
        control_layout = QHBoxLayout()  # Cria um layout horizontal para controles
        control_layout.setAlignment(Qt.AlignTop)  # Alinha o layout de controles ao topo
        self.image_label = QLabel(self)  # Cria um rótulo para exibir imagens
        self.image_label.setAlignment(Qt.AlignCenter)  # Centraliza o rótulo de imagem

        # Seção "Aplicar Filtro"
        filtro_layout = QVBoxLayout()  # Layout vertical para filtros
        filtro_label = QLabel("Aplicar Filtro de Convolução", self)  # Rótulo para a seção de filtros
        filtro_label.setFont(QFont("Arial", 12))  # Define a fonte do rótulo
        filtro_layout.addWidget(filtro_label)  # Adiciona o rótulo ao layout de filtros
        self.filtro_combo = QComboBox(self)  # ComboBox para seleção de filtros
        self.filtro_combo.addItems(["blur", "sharpen", "emboss", "laplacian", "canny", "sobel"])  # Adiciona itens ao ComboBox
        filtro_layout.addWidget(self.filtro_combo)  # Adiciona o ComboBox ao layout de filtros
        control_layout.addLayout(filtro_layout)  # Adiciona o layout de filtros ao layout de controles

        # Conectar a mudança de filtro à função de atualização 
        self.filtro_combo.currentIndexChanged.connect(self.alterar_filtro_video)  # Conecta a mudança de filtro à função de alteração

        # Seção "Geração de Imagens"
        geracao_layout = QVBoxLayout()  # Layout vertical para geração de imagens
        geracao_label = QLabel("Aplicar Fitro Cinza/Binário/Cores", self)  # Rótulo para a seção de geração de imagens
        geracao_label.setFont(QFont("Arial", 12))  # Define a fonte do rótulo
        geracao_layout.addWidget(geracao_label)  # Adiciona o rótulo ao layout de geração de imagens
        self.geracao_combo = QComboBox(self)  # ComboBox para seleção de geração de imagens
        self.geracao_combo.addItems(["cinza", "binario", "cores"])  # Adiciona itens ao ComboBox
        geracao_layout.addWidget(self.geracao_combo)  # Adiciona o ComboBox ao layout de geração de imagens
        control_layout.addLayout(geracao_layout)  # Adiciona o layout de geração de imagens ao layout de controles
        self.geracao_combo.currentIndexChanged.connect(self.aplicar_filtro_geracao)  # Conecta a mudança de filtro à função de aplicação

        # Seção "Vídeo"
        self.video_layout = QVBoxLayout()  # Layout vertical para vídeo
        self.video_label = QLabel("Vídeo", self)  # Rótulo para a seção de vídeo
        self.video_label.setFont(QFont("Arial", 12))  # Define a fonte do rótulo
        self.video_layout.addWidget(self.video_label)  # Adiciona o rótulo ao layout de vídeo

        btn_layout = QHBoxLayout()  # Layout horizontal para botões
        self.btn_voltar = QPushButton("Voltar", self)  # Botão para voltar no vídeo
        self.btn_avancar = QPushButton("Avançar", self)  # Botão para avançar no vídeo
        self.btn_inverter = QPushButton("Inverter", self)  # Botão para inverter o vídeo
        self.btn_inverter.clicked.connect(self.inverter)  # Conecta o botão de inverter à função inverter
        self.btn_pausar = QPushButton("Pausar", self)  # Botão para pausar o vídeo
        self.btn_pausar.clicked.connect(self.pausar)  # Conecta o botão de pausar à função pausar
        self.btn_parar = QPushButton("Parar", self)  # Botão para parar o vídeo
        self.btn_parar.clicked.connect(self.parar)  # Conecta o botão de parar à função parar
        self.btn_acelerar = QPushButton("Acelerar/Desacelerar", self)  # Botão para acelerar/desacelerar o vídeo
        
        self.btn_vel_025 = QPushButton("0.25x", self)  # Botão para velocidade 0.25x
        self.btn_vel_025.clicked.connect(lambda: self.set_velocidade_reproducao(0.25))  # Conecta o botão de 0.25x à função de setar velocidade
        self.btn_vel_1 = QPushButton("1x", self)  # Botão para velocidade 1x
        self.btn_vel_1.clicked.connect(lambda: self.set_velocidade_reproducao(1.0))  # Conecta o botão de 1x à função de setar velocidade
        self.btn_vel_2 = QPushButton("2x", self)  # Botão para velocidade 2x
        self.btn_vel_2.clicked.connect(lambda: self.set_velocidade_reproducao(2.0))  # Conecta o botão de 2x à função de setar velocidade
        
        btn_layout.addWidget(self.btn_voltar)  # Adiciona o botão de voltar ao layout de botões
        btn_layout.addWidget(self.btn_avancar)  # Adiciona o botão de avançar ao layout de botões
        btn_layout.addWidget(self.btn_inverter)  # Adiciona o botão de inverter ao layout de botões
        btn_layout.addWidget(self.btn_pausar)  # Adiciona o botão de pausar ao layout de botões
        btn_layout.addWidget(self.btn_parar)  # Adiciona o botão de parar ao layout de botões
        btn_layout.addWidget(self.btn_acelerar)  # Adiciona o botão de acelerar ao layout de botões
        btn_layout.addWidget(self.btn_vel_025)  # Adiciona o botão de 0.25x ao layout de botões
        btn_layout.addWidget(self.btn_vel_1)  # Adiciona o botão de 1x ao layout de botões
        btn_layout.addWidget(self.btn_vel_2)  # Adiciona o botão de 2x ao layout de botões

        self.video_layout.addLayout(btn_layout)  # Adiciona o layout de botões ao layout de vídeo

        self.video_duracao = QLabel("00:00 / 00:00", self)  # Rótulo para exibir a duração do vídeo
        self.video_layout.addWidget(self.video_duracao)  # Adiciona o rótulo de duração ao layout de vídeo
        control_layout.addLayout(self.video_layout)  # Adiciona o layout de vídeo ao layout de controles

        # Área de visualização
        self.scroll_area = QScrollArea(self)  # Cria uma área de rolagem para a imagem/vídeo
        self.scroll_area.setFixedSize(700, 500)  # Define o tamanho fixo da área de rolagem
        self.image_label.setAlignment(Qt.AlignCenter)  # Centraliza o rótulo de imagem
        self.scroll_area.setWidgetResizable(True)  # Permite que a área de rolagem seja redimensionável
        self.scroll_area.setWidget(self.image_label)  # Define o rótulo de imagem como widget da área de rolagem

        # Remover barras de rolagem para vídeos
        if self.tipo_arquivo == "Vídeo":
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Remove a barra de rolagem vertical
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Remove a barra de rolagem horizontal
            self.scroll_area.setAlignment(Qt.AlignCenter)  # Centraliza a área de rolagem
        else:
            self.video_label.setVisible(False)  # Oculta o rótulo de vídeo
            self.btn_voltar.setVisible(False)  # Oculta o botão de voltar
            self.btn_avancar.setVisible(False)  # Oculta o botão de avançar
            self.btn_inverter.setVisible(False)  # Oculta o botão de inverter
            self.btn_pausar.setVisible(False)  # Oculta o botão de pausar
            self.btn_parar.setVisible(False)  # Oculta o botão de parar
            self.btn_acelerar.setVisible(False)  # Oculta o botão de acelerar
            self.video_duracao.setVisible(False)  # Oculta o rótulo de duração
            self.btn_vel_025.setVisible(False)  # Oculta o botão de 0.25x
            self.btn_vel_1.setVisible(False)  # Oculta o botão de 1x
            self.btn_vel_2.setVisible(False)  # Oculta o botão de 2x

        main_layout.addLayout(control_layout)  # Adiciona o layout de controles ao layout principal
        self.setLayout(main_layout)  # Define o layout principal como layout da janela


# Layout de centralização
center_layout = QVBoxLayout()  # Cria um layout vertical para centralizar elementos
center_layout.addStretch(1)  # Adiciona um espaço flexível antes do widget principal
center_layout.addWidget(self.scroll_area, alignment=Qt.AlignCenter)  # Adiciona a área de rolagem ao layout, centralizada
center_layout.addStretch(1)  # Adiciona um espaço flexível depois do widget principal

main_layout.addLayout(control_layout)  # Adiciona o layout de controles ao layout principal
main_layout.addLayout(center_layout)  # Adiciona o layout central ao layout principal

print(f"Carregando imagem do caminho: {file_path}")  # Imprime mensagem de carregamento de imagem
if self.tipo_arquivo == "Imagem":
    self.original_image = cv2.imread(file_path)  # Lê a imagem do caminho fornecido
    if self.original_image is not None: 
        print("Imagem carregada com sucesso.")  # Imprime mensagem de sucesso
        self.carregar_imagem()  # Chama a função para carregar a imagem na interface
    else: 
        print("Falha ao carregar a imagem.")  # Imprime mensagem de falha
        
elif self.tipo_arquivo == "Vídeo":
    self.video_capture = cv2.VideoCapture(file_path)  # Captura o vídeo do caminho fornecido
    self.timer.timeout.connect(self.atualizar_quadro)  # Conecta o timer à função de atualização de quadros
    self.timer.start(30)  # Inicia o timer com intervalo de 30ms

central_widget = QWidget()  # Cria um widget central
central_widget.setLayout(main_layout)  # Define o layout principal como layout do widget central
self.setCentralWidget(central_widget)  # Define o widget central como widget principal da janela
self.setStyleSheet("background-color: #e6f2ff;")  # Define a cor de fundo da janela
    
self._config_botoes(main_layout)  # Chama a função para configurar os botões no layout principal

def opencv_imagem_qpixmap(self, image):
    altura, largura, canal = image.shape  # Obtém altura, largura e canais da imagem
    bytes_por_linha = canal * largura  # Calcula bytes por linha
    qimage = QImage(image.data, largura, altura, bytes_por_linha, QImage.Format_RGB888)  # Cria um QImage a partir dos dados da imagem
    pixmap = QPixmap.fromImage(qimage)  # Cria um QPixmap a partir do QImage
    return pixmap  # Retorna o QPixmap

def carregar_imagem(self):
    if self.original_image is not None:
        imagem = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)  # Converte a imagem de BGR para RGB
        pixmap = self.opencv_imagem_qpixmap(imagem)  # Converte a imagem OpenCV para QPixmap
        self.image_label.setPixmap(pixmap.scaled(1000, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Define o QPixmap no QLabel com escala
        self.image_label.resize(1000, 500)  # Redimensiona o QLabel

def concluir_selecao(self):
    if self.selecionando:
        self.selecionando = False  # Desativa o modo de seleção
        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)  # Calcula o ponto inicial da seleção
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)  # Calcula o ponto final da seleção
        
        # Adicionando logs para depuração
        print(f"Initial selection coordinates: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        
        # Ajustar as coordenadas considerando a proporção de zoom
        proporcao_x = self.original_image.shape[1] / self.image_label.pixmap().width()  # Calcula a proporção em x
        proporcao_y = self.original_image.shape[0] / self.image_label.pixmap().height()  # Calcula a proporção em y
        
        x1 = int(x1 * proporcao_x)  # Ajusta a coordenada x1
        y1 = int(y1 * proporcao_y)  # Ajusta a coordenada y1
        x2 = int(x2 * proporcao_x)  # Ajusta a coordenada x2
        y2 = int(y2 * proporcao_y)  # Ajusta a coordenada y2
        
        # Adicionando logs para depuração
        print(f"Scaled selection coordinates: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        
        if self.original_image is not None:
            self.cropped_image = self.original_image[y1:y2, x1:x2]  # Recorta a imagem original
            self.exibir_imagem(self.cropped_image)  # Exibe a imagem recortada
            print("Seleção concluída e imagem recortada armazenada.")
        else:
            self.cropped_image = None  # Define a imagem recortada como None
            print("Erro ao concluir a seleção: imagem original não encontrada.")

# Função exibir_imagem atualizada para usar a imagem original
def exibir_imagem(self, image):
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Converte a imagem de BGR para RGB
    pixmap = self.opencv_imagem_qpixmap(rgb_image)  # Converte a imagem OpenCV para QPixmap
    self.image_label.setPixmap(pixmap.scaled(self.scroll_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Define o QPixmap no QLabel com escala
    self.image_label.resize(self.scroll_area.size())  # Redimensiona o QLabel
    self.scroll_area.setWidget(self.image_label)  # Define o QLabel como widget da área de rolagem
    self.scroll_area.setWidgetResizable(True)  # Permite redimensionar a área de rolagem

def processar_video(self):
    cap = self.video_capture  # Obtém a captura de vídeo
    while True:
        rval, frame = cap.read()  # Lê um quadro do vídeo
        if not rval:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reinicia o vídeo se não puder ler o quadro
            continue

        if self.velocidade_reproducao == 0:
            self.velocidade_reproducao = 1  # Define a velocidade de reprodução como 1 se for 0

        img = self.escolhe_tipo(self.op, frame)  # Aplica o filtro selecionado ao quadro
        cv2.imshow('frame', img)  # Exibe o quadro processado

        key = cv2.waitKey(int(1000 / self.velocidade_reproducao)) & 0xFF  # Espera por uma tecla pressionada
        if key == ord('q'):
            break  # Encerra o loop se a tecla 'q' for pressionada
        elif key == ord('z'):
            self.op = "z"  # Seleciona a operação 'z'
        elif key == ord('n'):
            self.op = ""  # Limpa a operação
        elif key == ord('p'):
            self.velocidade_reproducao = -1  # Define a velocidade de reprodução como -1
            self.op = 'p'  # Seleciona a operação 'p'
        elif key == ord('v'):
            self.velocidade_reproducao = 10  # Define a velocidade de reprodução como 10
        elif key == ord('i'):
            self.i = self.cont  # Define o início do intervalo de recorte
        elif key == ord('f') and self.i != 0:
            self.f = self.cont  # Define o fim do intervalo de recorte
        elif key == ord('-'):
            self.velocidade_reproducao = max(self.velocidade_reproducao + 5, 1)  # Aumenta a velocidade de reprodução
        elif key == ord('+'):
            self.velocidade_reproducao = max(self.velocidade_reproducao - 5, 1)  # Diminui a velocidade de reprodução
        elif key == ord('s'):
            if self.op == 'p':
                cv2.imwrite(path_salvar+'frame_alterado.jpg', img)  # Salva o quadro alterado
            if self.i != 0 and self.f != 0:
                break  # Encerra o loop se o intervalo de recorte estiver definido

        print(self.cont)  # Imprime o contador de quadros
        self.cont += 1
    cap.release()  # Libera a captura de vídeo
    cv2.destroyAllWindows()  # Fecha todas as janelas abertas
    print('Finalizou a geração dos frames.')  # Imprime mensagem de finalização
    if self.i != 0 and self.f != 0:
        self.salvar_frames(self.i, self.f)  # Salva os frames do intervalo definido

def atualizar_quadro(self):
    ret, frame = self.video_capture.read()  # Lê um quadro do vídeo
    if ret:  # Se a leitura do quadro for bem-sucedida
        if self.aplicar_filtro_video:  # Se o filtro de vídeo deve ser aplicado
            frame = self.aplicar_filtro(frame, self.filtro_selecionado_video)  # Aplica o filtro selecionado ao quadro
        
        imagem = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Converte o quadro de BGR para RGB
        altura, largura, canal = imagem.shape  # Obtém as dimensões e canais da imagem
        passo = canal * largura  # Calcula os bytes por linha
        qimage = QImage(imagem.data, largura, altura, passo, QImage.Format_RGB888)  # Cria um QImage a partir dos dados da imagem
        pixmap = QPixmap.fromImage(qimage)  # Cria um QPixmap a partir do QImage

        self.image_label.setPixmap(pixmap.scaled(self.scroll_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Define o QPixmap no QLabel com escala
        self.image_label.setFixedSize(self.scroll_area.size())  # Define o tamanho fixo do QLabel
        self.scroll_area.setWidget(self.image_label)  # Define o QLabel como widget da área de rolagem
    else:
        self.timer.stop()  # Para o timer se a leitura do quadro falhar
        self.video_capture.release()  # Libera a captura de vídeo

def voltar(self):
    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, max(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES) - 30, 0))  # Volta 30 quadros no vídeo

def avancar(self):
    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.video_capture.get(cv2.CAP_PROP_POS_FRAMES) + 30)  # Avança 30 quadros no vídeo

def inverter(self):
    self.invertido = not self.invertido  # Inverte o estado de reprodução
    print(f"Inversão do vídeo: {'Ativada' if self.invertido else 'Desativada'}")  # Imprime o estado de inversão

    # Reiniciar o temporizador para ajustar o intervalo do quadro corretamente
    if self.invertido:
        self.timer.stop()  # Para o timer
        self.timer.start(int(1000 / (self.velocidade_reproducao * 30)))  # Reinicia o timer com a nova velocidade
    else:
        self.timer.stop()  # Para o timer
        self.timer.start(int(1000 / (self.velocidade_reproducao * 30)))  # Reinicia o timer com a nova velocidade

    # Inicialização do temporizador
    self.timer = QTimer()  # Cria um novo QTimer
    self.timer.timeout.connect(self.atualizar_quadro)  # Conecta o timeout do timer à função atualizar_quadro
    self.timer.start(int(1000 / (self.velocidade_reproducao * 30)))  # Inicia o timer com o intervalo baseado na velocidade de reprodução

def reproduzir(self):
    # Se o vídeo está invertido
    if self.invertido:
        frame_pos = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)  # Obtém a posição atual do quadro
        if frame_pos <= 0:  # Se o vídeo está no início, rebobina para o final
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
        else:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_pos - 1)  # Volta um quadro
    else:
        # Reprodução normal
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, self.video_capture.get(cv2.CAP_PROP_POS_FRAMES) + 1)  # Avança um quadro

    if not self.timer.isActive():
        self.timer.start(int(1000 / (self.velocidade_reproducao * 30)))  # Inicia o timer se não estiver ativo

def parar(self):
    if self.video_capture is not None:
        self.video_capture.release()  # Libera a captura de vídeo
    self.timer.stop()  # Para o timer
    self.image_label.clear()  # Limpa o QLabel

def pausar(self):
    self.timer.stop()  # Para o timer

def set_velocidade_reproducao(self, velocidade):
    self.velocidade_reproducao = velocidade  # Define a nova velocidade de reprodução
    self.timer.start(int(1000 / (self.velocidade_reproducao * 30)))  # Reinicia o timer com o novo intervalo

def closeEvent(self, event):
    if self.video_capture is not None:
        self.video_capture.release()  # Libera a captura de vídeo
    super().closeEvent(event)  # Chama o método closeEvent da classe base

def voltar(self):
    self.close()  # Fecha a janela atual
    self.janela_principal.show()  # Mostra a janela principal

def _config_botoes(self, layout):
    btn_layout = QHBoxLayout()  # Cria um layout horizontal para os botões
    btn_estilo = {  # Define o estilo dos botões
        "font-family": "Arial",
        "font-size": "15px",
        "color": "#000000",
        "background-color": "#007acc",
        "padding": "5px 20px",
        "margin": "5px",
        "width": "10px",
        "height": "10px"
    }

    self.btn_voltar_inf = self._criar_btn("Voltar", btn_estilo, self.voltar)  # Cria o botão "Voltar"
    self.btn_zoom_mais = self._criar_btn("Zoom+", btn_estilo, self.zoom_mais)  # Cria o botão "Zoom+"
    self.btn_zoom_menos = self._criar_btn("Zoom-", btn_estilo, self.zoom_menos)  # Cria o botão "Zoom-"
    self.btn_aplicar_filtro = self._criar_btn("Aplicar Filtro", btn_estilo, self.aplicar_filtro_convolucao_imagem)  # Cria o botão "Aplicar Filtro"
    self.btn_desfaz_selecao = self._criar_btn("Desfazer Seleção", btn_estilo, self.desfazer_selecao)  # Cria o botão "Desfazer Seleção"
    self.btn_salvar = self._criar_btn("Salvar", btn_estilo, self.salvar_recorte)  # Cria o botão "Salvar"
    self.btn_sair = self._criar_btn("Sair", btn_estilo, self.close)  # Cria o botão "Sair"

    btn_layout.addWidget(self.btn_voltar_inf)  # Adiciona o botão "Voltar" ao layout de botões
    btn_layout.addWidget(self.btn_zoom_mais)  # Adiciona o botão "Zoom+" ao layout de botões
    btn_layout.addWidget(self.btn_zoom_menos)  # Adiciona o botão "Zoom-" ao layout de botões
    btn_layout.addWidget(self.btn_aplicar_filtro)  # Adiciona o botão "Aplicar Filtro" ao layout de botões
    btn_layout.addWidget(self.btn_desfaz_selecao)  # Adiciona o botão "Desfazer Seleção" ao layout de botões
    btn_layout.addWidget(self.btn_salvar)  # Adiciona o botão "Salvar" ao layout de botões
    btn_layout.addWidget(self.btn_sair)  # Adiciona o botão "Sair" ao layout de botões

    layout.addLayout(btn_layout)  # Adiciona o layout de botões ao layout principal

# Função para desfazer a seleção, zoom e filtros
def desfazer_selecao(self):
    if self.original_image is not None:  # Verifica se há uma imagem original carregada
        print("Desfazendo seleção, zoom e filtros, retornando à imagem original.")
        self.cropped_image = None  # Remove a imagem cortada
        self.rect_inicio_ponto = None  # Reseta o ponto inicial do retângulo de seleção
        self.rect_fim_ponto = None  # Reseta o ponto final do retângulo de seleção
        self.zoom_level = 1.0  # Reseta o nível de zoom
        self.imagem_convolucao = None  # Reseta a imagem convolucionada
        self.imagem_bin_cinza_cores = None  # Reseta a imagem binária/cinza/cores
        self.original_image = self.imagem_antes_filtro  # Restaura a imagem original antes do filtro
        self.aplicar_tamanho_original()  # Reseta o zoom e exibe a imagem original
        self.exibir_imagem(self.original_image)  # Exibe a imagem original
    else:
        print("Nenhuma imagem carregada para desfazer a seleção.")  # Informa que não há imagem carregada

def aplicar_filtro_geracao(self):
    if self.original_image is not None:  # Verifica se há uma imagem original carregada
        filtro_selecionado = self.geracao_combo.currentText()  # Obtém o filtro selecionado no ComboBox
        print("Aplicando filtro de geração de imagem:", filtro_selecionado)
        self.imagem_bin_cinza_cores = self.aplicar_filtro_bin_cinz_cores(self.original_image, filtro_selecionado)  # Aplica o filtro de geração de imagem
        self.exibir_imagem(self.imagem_bin_cinza_cores)  # Exibe a imagem filtrada
        # Atualizar a imagem original para a imagem filtrada
        self.original_image = self.imagem_bin_cinza_cores.copy()  # Atualiza a imagem original com a imagem filtrada
    else:
        print("Nenhuma imagem carregada para aplicar o filtro de geração.")  # Informa que não há imagem carregada

def aplicar_filtro_bin_cinz_cores(self, image, filter_type):
    print("Entrando na função aplicar_filtro_bin_cinz_cores")
    cv_image = np.array(image)  # Converte a imagem para um array NumPy
    if filter_type == "binario":
        _, filtered_image = cv2.threshold(cv_image, 127, 255, cv2.THRESH_BINARY)  # Aplica o filtro binário
    elif filter_type == "cinza":
        filtered_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)  # Aplica o filtro de escala de cinza
    elif filter_type == "cores":
        filtered_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)  # Aplica o filtro de cores (HSV)
    else:
        filtered_image = cv_image  # Caso contrário, mantém a imagem original
    print(f"Filtro {filter_type} aplicado.")  # Informa que o filtro foi aplicado
    return filtered_image  # Retorna a imagem filtrada

# Modificar a função aplicar_filtro_convolucao para armazenar a imagem original antes de aplicar o filtro
def aplicar_filtro_convolucao_imagem(self):
    if self.original_image is not None:  # Verifica se há uma imagem original carregada
        filtro_selecionado = self.filtro_combo.currentText()  # Obtém o filtro selecionado no ComboBox
        try:
            # Armazenar a imagem original antes de aplicar o filtro
            self.imagem_antes_filtro = self.original_image.copy()  # Copia a imagem original
            
            filtered_image = self.aplicar_filtro(self.original_image, filtro_selecionado)  # Aplica o filtro convolucional
            filtered_image_cv = np.array(filtered_image)  # Converte a imagem filtrada para um array NumPy

            if filtro_selecionado in ["laplacian", "sobel", "scharr", "prewitt"]:
                filtered_image_cv = cv2.normalize(filtered_image_cv, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)  # Normaliza a imagem filtrada

            self.exibir_imagem(filtered_image_cv)  # Exibe a imagem filtrada
            self.original_image = filtered_image_cv  # Atualiza a imagem original com a imagem filtrada
            self.imagem_convolucao = filtered_image_cv  # Armazena a imagem convolucionada

            print(f"Filtro {filtro_selecionado} aplicado com sucesso.")  # Informa que o filtro foi aplicado com sucesso
        except Exception as e:
            print(f"Erro ao aplicar filtro: {e}")  # Informa um erro ao aplicar o filtro
    else:
        print("Nenhuma imagem carregada para aplicar filtro.")  # Informa que não há imagem carregada

def alterar_filtro_video(self): 
    self.aplicar_filtro_video = True  # Ativa a aplicação do filtro no vídeo
    self.filtro_selecionado_video = self.filtro_combo.currentText()  # Obtém o filtro selecionado no ComboBox

def aplicar_filtro(self, image, filter_type):
    cv_image = np.array(image)  # Converte a imagem para um array NumPy
    
    if filter_type == "blur":
        print("Aplicando filtro: blur")
        filtered_image = cv2.GaussianBlur(cv_image, (15, 15), 0)  # Aplica o filtro Gaussian Blur
    elif filter_type == "sharpen":
        print("Aplicando filtro: sharpen")
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Define o kernel para o filtro de sharpening
        filtered_image = cv2.filter2D(cv_image, -1, kernel)  # Aplica o filtro de sharpening
    elif filter_type == "emboss":
        print("Aplicando filtro: emboss")
        kernel = np.array([[0, -1, -1], [1, 0, -1], [1, 1, 0]])  # Define o kernel para o filtro de emboss
        filtered_image = cv2.filter2D(cv_image, -1, kernel)  # Aplica o filtro de emboss
    elif filter_type == "laplacian":
        print("Aplicando filtro: laplacian")
        filtered_image = cv2.Laplacian(cv_image, cv2.CV_64F)  # Aplica o filtro Laplacian
    elif filter_type == "canny":
        print("Aplicando filtro: canny")
        filtered_image = cv2.Canny(cv_image, 100, 200)  # Aplica o filtro Canny
    elif filter_type == "sobel":
        print("Aplicando filtro: sobel")
        filtered_image = cv2.Sobel(cv_image, cv2.CV_64F, 1, 0, ksize=5)  # Aplica o filtro Sobel
    elif filter_type == "median_blur":
        print("Aplicando filtro: median_blur")
        filtered_image = cv2.medianBlur(cv_image, 5)  # Aplica o filtro Median Blur
    elif filter_type == "bilateral_filter":
        print("Aplicando filtro: bilateral_filter")
        filtered_image = cv2.bilateralFilter(cv_image, 9, 75, 75)  # Aplica o filtro Bilateral Filter
    elif filter_type == "scharr":
        print("Aplicando filtro: scharr")
        filtered_image = cv2.Scharr(cv_image, cv2.CV_64F, 1, 0)  # Aplica o filtro Scharr
    elif filter_type == "prewitt":
        print("Aplicando filtro: prewitt")
        kernelx = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])  # Define o kernel para o filtro Prewitt no eixo x
        kernely = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])  # Define o kernel para o filtro Prewitt no eixo y
        filtered_image_x = cv2.filter2D(cv_image, -1, kernelx)  # Aplica o filtro Prewitt no eixo x
        filtered_image_y = cv2.filter2D(cv_image, -1, kernely)  # Aplica o filtro Prewitt no eixo y
        filtered_image = cv2.addWeighted(filtered_image_x, 0.5, filtered_image_y, 0.5, 0)  # Combina os filtros aplicados nos eixos x e y
    else:
        filtered_image = cv_image  # Caso contrário, mantém a imagem original

    print(f"Filtro {filter_type} aplicado.")  # Informa que o filtro foi aplicado
    return filtered_image  # Retorna a imagem filtrada

def _criar_btn(self, texto, estilo, chamada_retorno=None):
    btn = QPushButton(texto, self)  # Cria um botão com o texto fornecido
    btn.setStyleSheet(f""

def zoom_mais(self):
    if self.original_image is not None:  # Verifica se há uma imagem original carregada
        print(f"Zoom+: Level Before: {self.zoom_level}")  # Log do nível de zoom antes de aumentar
        self.zoom_level = min(self.zoom_level * 1.2, 4.0)  # Aumenta o nível de zoom por um fator de 1.2, limitando a 4.0
        self.aplicar_zoom_customizado()  # Aplica o zoom customizado
    
def zoom_menos(self):
    if self.original_image is not None:  # Verifica se há uma imagem original carregada
        print(f"Zoom-: Level Before: {self.zoom_level}")  # Log do nível de zoom antes de diminuir
        self.zoom_level = max(self.zoom_level / 1.2, 1.0)  # Diminui o nível de zoom por um fator de 1.2, limitando a 1.0
        if self.zoom_level <= 1.01:  # Pequena margem para garantir que volte ao original
            self.zoom_level = 1.0  # Reseta o nível de zoom para 1.0
            self.aplicar_tamanho_original()  # Aplica o tamanho original da imagem
        else:
            self.aplicar_zoom_customizado()  # Aplica o zoom customizado

def aplicar_tamanho_original(self):
    if self.original_image is not None:  # Verifica se há uma imagem original carregada
        try:
            original_img_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)  # Converte a imagem de BGR para RGB
            pixmap = self.opencv_imagem_qpixmap(original_img_rgb)  # Converte a imagem OpenCV para QPixmap
            self.image_label.setPixmap(pixmap.scaled(self.scroll_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))  # Define o QPixmap no QLabel com escala
            self.image_label.resize(self.scroll_area.size())  # Redimensiona o QLabel
            self.scroll_area.setWidget(self.image_label)  # Define o QLabel como widget da área de rolagem
            self.scroll_area.setWidgetResizable(True)  # Permite redimensionar a área de rolagem
            print("Imagem redefinida para o tamanho original.")  # Log de sucesso
        except Exception as e:
            print(f"Erro ao redefinir para o tamanho original: {e}")  # Log de erro
    else:
        print("Nenhuma imagem carregada para redefinir.")  # Log informando a ausência de imagem

def aplicar_zoom_customizado(self):
    if self.original_image is not None:  # Verifica se há uma imagem original carregada
        try:
            altura, largura, _ = self.original_image.shape  # Obtém a altura e a largura da imagem
            nova_altura = int(altura * self.zoom_level)  # Calcula a nova altura com base no nível de zoom
            nova_largura = int(largura * self.zoom_level)  # Calcula a nova largura com base no nível de zoom
            zoomed_img = cv2.resize(self.original_image, (nova_largura, nova_altura), interpolation=cv2.INTER_LINEAR)  # Redimensiona a imagem
            zoomed_img_rgb = cv2.cvtColor(zoomed_img, cv2.COLOR_BGR2RGB)  # Converte a imagem redimensionada de BGR para RGB
            pixmap = self.opencv_imagem_qpixmap(zoomed_img_rgb)  # Converte a imagem OpenCV para QPixmap
            self.image_label.setPixmap(pixmap)  # Define o QPixmap no QLabel
            self.image_label.resize(nova_largura, nova_altura)  # Redimensiona o QLabel
            self.scroll_area.setWidget(self.image_label)  # Define o QLabel como widget da área de rolagem
            self.scroll_area.setWidgetResizable(True)  # Permite redimensionar a área de rolagem
            self.scroll_area.setFixedSize(1000, 500)  # Define o tamanho fixo da área de rolagem
            print(f"Zoom aplicado: {nova_largura}x{nova_altura}")  # Log do novo tamanho da imagem
        except Exception as e:
            print(f"Erro ao aplicar zoom: {e}")  # Log de erro
    else:
        print("Nenhuma imagem carregada para aplicar zoom")  # Log informando a ausência de imagem

def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:  # Verifica se o botão esquerdo do mouse foi pressionado
        self.rect_inicio_ponto = event.pos()  # Armazena a posição inicial do retângulo de seleção
        self.rect_fim_ponto = None  # Reseta a posição final do retângulo de seleção

def mouseMoveEvent(self, event):
    if self.rect_inicio_ponto:  # Verifica se a posição inicial do retângulo foi definida
        self.rect_fim_ponto = event.pos()  # Atualiza a posição final do retângulo
        self.update()  # Atualiza a interface gráfica

def mouse_release_event(self, event):
    if event.button() == Qt.LeftButton:  # Verifica se o botão esquerdo do mouse foi solto
        if self.selecionando:  # Verifica se o modo de seleção está ativo
            self.end_x = event.pos().x()  # Armazena a posição x final do retângulo de seleção
            self.end_y = event.pos().y()  # Armazena a posição y final do retângulo de seleção
            print(f"Mouse released at: {self.end_x}, {self.end_y}")  # Log para depuração
            self.atualizar_selecao()  # Atualiza a seleção na interface
            self.concluir_selecao()  # Conclui a seleção

def atualizar_selecao(self):
    if self.original_image is not None and self.selecionando:  # Verifica se há uma imagem carregada e o modo de seleção está ativo
        temp_image = self.original_image.copy()  # Faz uma cópia da imagem original
        x1, y1 = self.start_x, self.start_y  # Obtém as coordenadas iniciais da seleção
        x2, y2 = self.end_x, self.end_y  # Obtém as coordenadas finais da seleção
        # Certifique-se de que as coordenadas estejam dentro dos limites
        x1, x2 = max(0, x1), min(temp_image.shape[1], x2)  # Ajusta as coordenadas x para ficarem dentro dos limites da imagem
        y1, y2 = max(0, y1), min(temp_image.shape[0], y2)  # Ajusta as coordenadas y para ficarem dentro dos limites da imagem
        # Desenhar o retângulo vermelho
        cv2.rectangle(temp_image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Desenha o retângulo na imagem temporária
        self.exibir_imagem(temp_image)  # Exibe a imagem temporária com o retângulo
        print(f"Drawing rectangle from ({x1}, {y1}) to ({x2}, {y2})")  # Log para depuração
    else:
        print("Erro: Coordenadas inválidas ou imagem não carregada.")  # Log de erro

def salvar_recorte(self):
    if self.rect_inicio_ponto and self.rect_fim_ponto:  # Verifica se há uma seleção definida
        # Posição do scroll
        scroll_x = self.scroll_area.horizontalScrollBar().value()  # Obtém o valor da barra de rolagem horizontal
        scroll_y = self.scroll_area.verticalScrollBar().value()  # Obtém o valor da barra de rolagem vertical

        # Coordenadas de seleção ajustadas pela posição do scroll
        x1, y1 = self.rect_inicio_ponto.x() + scroll_x, self.rect_inicio_ponto.y() + scroll_y  # Ajusta as coordenadas iniciais da seleção
        x2, y2 = self.rect_fim_ponto.x() + scroll_x, self.rect_fim_ponto.y() + scroll_y  # Ajusta as coordenadas finais da seleção

        x1, x2 = sorted([x1, x2])  # Ordena as coordenadas x para garantir a seleção correta
        y1, y2 = sorted([y1, y2])  # Ordena as coordenadas y para garantir a seleção correta

        print(f"Before scaling: x1={x1}, y1={y1}, x2={x2}, y2={y2}")  # Log para depuração

        # Proporção de escala da imagem original em relação ao tamanho da image_label
        proporcao_x = self.original_image.shape[1] / self.image_label.pixmap().width()  # Calcula a proporção em x
        proporcao_y = self.original_image.shape[0] / self.image_label.pixmap().height()  # Calcula a proporção em y

        x1 = int(x1 * proporcao_x)  # Ajusta a coordenada x1 com a proporção
                proporcao_y = self.original_image.shape[0] / self.image_label.pixmap().height()  # Calcula a proporção em y

        x1 = int(x1 * proporcao_x)  # Ajusta a coordenada x1 com a proporção
        y1 = int(y1 * proporcao_y)  # Ajusta a coordenada y1 com a proporção
        x2 = int(x2 * proporcao_x)  # Ajusta a coordenada x2 com a proporção
        y2 = int(y2 * proporcao_y)  # Ajusta a coordenada y2 com a proporção

        print(f"After scaling: x1={x1}, y1={y1}, x2={x2}, y2={y2}")  # Log para depuração

        # Aplicar o recorte na imagem atual (que pode ser a imagem filtrada e ampliada)
        recorte = self.original_image[y1:y2, x1:x2]  # Recorta a imagem original usando as coordenadas ajustadas

        # Salvar a imagem recortada e com qualquer filtro aplicado
        path_salvar = QFileDialog.getExistingDirectory(self, "C:/Users/SeuUsuario/Desktop")  # Abre um diálogo para selecionar o diretório de salvamento
        if path_salvar:
            file_path = f"{path_salvar}/imagem_recortada.jpg"  # Define o caminho completo para salvar a imagem recortada
            cv2.imwrite(file_path, recorte)  # Salva a imagem recortada no caminho especificado
            print(f"Imagem recortada salva em: {file_path}")  # Log do local de salvamento

        self.rect_inicio_ponto = None  # Reseta a posição inicial do retângulo de seleção
        self.rect_fim_ponto = None  # Reseta a posição final do retângulo de seleção
        self.update()  # Atualiza a interface gráfica
    else:
        print("Nenhuma área recortada para salvar.")  # Log informando que não há área recortada para salvar

def paintEvent(self, event):
    super().paintEvent(event)  # Chama o método paintEvent da classe base
    if self.rect_inicio_ponto and self.rect_fim_ponto:  # Verifica se há uma seleção definida
        painter = QPainter(self)  # Cria um objeto QPainter para desenhar na interface
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))  # Define a caneta para desenhar o retângulo
        rect = QRect(self.rect_inicio_ponto, self.rect_fim_ponto)  # Cria um objeto QRect com as coordenadas de seleção
        painter.drawRect(rect.normalized())  # Desenha o retângulo normalizado (ajustado para as coordenadas corretas)


def selecionar_arq(parent, modo, tipo_arquivo):
    options = QFileDialog.Options()  # Cria opções para o diálogo de arquivo
    options |= QFileDialog.DontUseNativeDialog  # Define a opção para não usar o diálogo nativo
    file_dialog = QFileDialog()  # Cria um diálogo de arquivo
    file_dialog.setDirectory(os.path.expanduser("C:Users/walla/documents/"))  # Define o diretório inicial do diálogo de arquivo
    file_path, _ = file_dialog.getOpenFileName(
        parent, 
        "Selecionar Arquivo",  # Título do diálogo de arquivo
        "",  # Diretório inicial (aqui vazio)
        "Todos os Arquivos (*);;Imagens (*.png *.jpg *.jpeg);;Vídeos (*.mp4 *.avi)",  # Filtros para tipos de arquivos
        options=options  # Passa as opções definidas anteriormente
    )
    if file_path:  # Se um arquivo foi selecionado
        file_info = QFileInfo(file_path)  # Obtém informações sobre o arquivo
        extension = file_info.suffix().lower()  # Obtém a extensão do arquivo em letras minúsculas
        if extension in ['png', 'jpg', 'jpeg']:
            tipo_arquivo = "Imagem"  # Define o tipo de arquivo como imagem
        elif extension in ['mp4', 'avi']:
            tipo_arquivo = "Vídeo"  # Define o tipo de arquivo como vídeo
        else:
            print(f"Formato de arquivo não suportado: {extension}")  # Informa que o formato de arquivo não é suportado
            return  # Sai da função
        parent.abrir_segunda_janela(file_path, 100, 100, tipo_arquivo)  # Abre a segunda janela passando o caminho do arquivo, coordenadas x e y, e o tipo de arquivo


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()  # Inicializa a classe base QMainWindow
        self.setWindowTitle("Manipulação de Imagens e Vídeos")  # Define o título da janela principal
        self.setGeometry(100, 100, 1000, 700)  # Define a posição e o tamanho da janela principal
        self._setup_ui()  # Chama o método para configurar a interface do usuário
    
    def _setup_ui(self):  # Método para configurar a interface do usuário
        self.setStyleSheet("background-color: #e6f2ff;")  # Define a cor de fundo da janela principal
        self.setFixedSize(self.size())  # Define o tamanho fixo da janela principal
        self._centralizar_tela()  # Chama o método para centralizar a janela na tela
        self._setup_fontes()  # Chama o método para configurar as fontes
        self._setup_widgets()  # Chama o método para configurar os widgets
        self._setup_bottoes()  # Chama o método para configurar os botões

    def _setup_fontes(self):  # Método para configurar as fontes
        self.label_fonte = QFont("Arial", 10)  # Define a fonte para os rótulos
        self.label_fonte.setBold(True)  # Define a fonte dos rótulos como negrito
        self.combo_fonte = QFont("Arial", 10)  # Define a fonte para os ComboBoxes
        self.btn_fonte = QFont("Arial", 12)  # Define a fonte para os botões

    def _setup_widgets(self):  # Método para configurar os widgets
        self.tipo_arquivo_label = QLabel("Tipo de Arquivo", self)  # Cria um rótulo para "Tipo de Arquivo"
        self.tipo_arquivo_label.setFont(self.label_fonte)  # Define a fonte do rótulo
        self.tipo_arquivo_label.setStyleSheet("color: #333333; padding: 10px; background-color: #cce6ff; margin: 1px;")  # Define o estilo do rótulo
        self.tipo_arquivo_label.adjustSize()  # Ajusta o tamanho do rótulo ao conteúdo
        self.tipo_arquivo_label.move(200, 150)  # Move o rótulo para a posição (200, 150)

        self.tipo_arquivo = QComboBox(self)  # Cria um ComboBox para selecionar o tipo de arquivo
        self.tipo_arquivo.addItems(["Imagem", "Vídeo"])  # Adiciona itens ao ComboBox
        self.tipo_arquivo.setFont(self.combo_fonte)  # Define a fonte do ComboBox
        self.tipo_arquivo.setStyleSheet("color: #333333; padding: 10px; background-color: #e6f2ff; margin: 1px;")  # Define o estilo do ComboBox
        self.tipo_arquivo.setMinimumContentsLength(10)  # Define o comprimento mínimo do conteúdo do ComboBox
        self.tipo_arquivo.setSizeAdjustPolicy(QComboBox.AdjustToContents)  # Ajusta o tamanho do ComboBox ao conteúdo
        self.tipo_arquivo.move(200, 200)  # Move o ComboBox para a posição (200, 200)

        self.modo_label = QLabel("Selecione Modo", self)  # Cria um rótulo para "Selecione Modo"
        self.modo_label.setFont(self.label_fonte)  # Define a fonte do rótulo
        self.modo_label.setStyleSheet("color: #333333; padding: 10px; background-color: #cce6ff; margin: 0px;")  # Define o estilo do rótulo
        self.modo_label.adjustSize()  # Ajusta o tamanho do rótulo ao conteúdo
        self.modo_label.move(670, 150)  # Move o rótulo para a posição (670, 150)

        self.modo = QComboBox(self)  # Cria um ComboBox para selecionar o modo
        self.modo.addItems(["Independente", "Cascata"])  # Adiciona itens ao ComboBox
        self.modo.setFont(self.combo_fonte)  # Define a fonte do ComboBox
        self.modo.setStyleSheet("color: #333333; padding: 10px; background-color: #e6f2ff; margin: 1px;")  # Define o estilo do ComboBox
        self.modo.setMinimumContentsLength(10)  # Define o comprimento mínimo do conteúdo do ComboBox
        self.modo.setSizeAdjustPolicy(QComboBox.AdjustToContents)  # Ajusta o tamanho do ComboBox ao conteúdo
        self.modo.move(670, 200)  # Move o ComboBox para a posição (670, 200)

    def _setup_bottoes(self):  # Método para configurar os botões
       self.btn_avancar = QPushButton("Avançar", self)  # Cria um botão "Avançar"
       self.btn_avancar.setFont(self.btn_fonte)  # Define a fonte do botão
       self.btn_avancar.setStyleSheet("background-color: #007acc; color: #ffffff;")  # Define o estilo do botão
       self.btn_avancar.resize(self.btn_avancar.sizeHint())  # Redimensiona o botão para o tamanho recomendado
       self.btn_avancar.move(200, 600)  # Move o botão para a posição (200, 600)
       self.btn_avancar.clicked.connect(self.avancar)  # Conecta o clique do botão ao método "avancar"

       self.btn_sair = QPushButton("Sair", self)  # Cria um botão "Sair"
       self.btn_sair.setFont(self.btn_fonte)  # Define a fonte do botão
       self.btn_sair.setStyleSheet("background-color: red;  padding: 10px 45px;")  # Define o estilo do botão
       self.btn_sair.resize(self.btn_sair.sizeHint())  # Redimensiona o botão para o tamanho recomendado
       self.btn_sair.move(670, 600)  # Move o botão para a posição (670, 600)
       self.btn_sair.clicked.connect(self.close)  # Conecta o clique do botão ao método "close"

    def avancar(self):
       modo = self.modo.currentText()  # Obtém o texto atual do ComboBox "modo"
       tipo_arquivo = self.tipo_arquivo.currentText()  # Obtém o texto atual do ComboBox "tipo_arquivo"
       selecionar_arq(self, modo, tipo_arquivo)  # Chama a função para selecionar o arquivo

    def abrir_segunda_janela(self, file_path, x, y, tipo_arquivo):
        self.segunda_janela = JanelaSecundaria(file_path, x, y, tipo_arquivo, self)  # Cria uma nova instância de JanelaSecundaria
        self.segunda_janela.showMaximized()  # Exibe a segunda janela maximizada

    def _centralizar_tela(self):  # Método para centralizar a janela na tela
        qt_rectangle = self.frameGeometry()  # Obtém a geometria da janela principal
        center_point = QDesktopWidget().availableGeometry().center()  # Obtém o ponto central da área disponível
        qt_rectangle.moveCenter(center_point)  # Move o retângulo para o ponto central
        self.move(qt_rectangle.topLeft())  # Move a janela para o topo esquerdo do retângulo



from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox, QPushButton, 
                            QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, 
                            QSizePolicy, QFrame, QDesktopWidget, QScrollArea)

QApplication: Classe necessária para criar uma aplicação GUI.

QMainWindow: Classe base para a janela principal de uma aplicação.

QLabel: Widget usado para exibir texto ou imagem.

QComboBox: Widget que exibe uma lista suspensa de itens.

QPushButton: Widget que representa um botão.

QFileDialog: Widget de diálogo para abrir e salvar arquivos.

QWidget: Classe base para todos os widgets de interface.

QVBoxLayout: Layout que organiza widgets verticalmente.

QHBoxLayout: Layout que organiza widgets horizontalmente.

QSpacerItem: Item de espaçamento usado em layouts.

QSizePolicy: Define políticas de redimensionamento de widgets.

QFrame: Widget de quadro que pode ter bordas e título.

QDesktopWidget: Classe para obter informações sobre a área de trabalho do sistema.

QScrollArea: Widget que fornece uma área de rolagem para widgets maiores.



from PyQt5.QtCore import Qt, QRect, QPoint, QTimer, QFileInfo
QPainter: Classe usada para desenhar gráficos.

QPen: Classe que define canetas para desenhar bordas de formas.

QImage: Classe para manipulação de imagens.

QPixmap: Classe para manipulação de imagens otimizadas para exibição na tela.

QFont: Classe que define fontes para texto.


import cv2

Biblioteca OpenCV para manipulação de imagens e vídeos.

import sys

Módulo para acessar variáveis e funções do interpretador Python.

import os

Módulo que fornece uma maneira de usar funcionalidades dependentes do sistema operacional.

import numpy as np

Biblioteca NumPy para manipulação de arrays e operações matemáticas.

from PIL import Image

Biblioteca Pillow (PIL fork) para manipulação de imagens.


def pil_imagem_qpixmap(image):
    """Converte uma imagem PIL para QPixmap"""
    image = image.convert("RGBA")  # Converte a imagem PIL para o formato RGBA
    date = image.tobytes("raw", "RGBA")  # Converte os dados da imagem para bytes no formato RGBA
    qimage = QImage(date, image.width, image.height, QImage.Format_RGBA8888)  # Cria um QImage a partir dos bytes de dados da imagem, largura, altura e formato RGBA
    pixmap = QPixmap.fromImage(qimage)  # Converte o QImage para QPixmap
    return pixmap  # Retorna o QPixmap


def zoom(img, yi, yf, xi, xf):
    z = img[yi:yf, xi:xf]  # Recorta a imagem `img` para a região delimitada pelas coordenadas (yi, yf) e (xi, xf)
    return z  # Retorna a imagem recortada


if __name__ == "__main__":  # Verifica se o script está sendo executado diretamente (e não importado como módulo)
    app = QApplication(sys.argv)  # Cria uma instância de QApplication que gerencia a aplicação GUI
    janela_principal = JanelaPrincipal()  # Cria uma instância da janela principal
    janela_principal.show()  # Exibe a janela principal
    app.exec_()  # Inicia o loop de eventos da aplicação (mantém a aplicação em execução)


