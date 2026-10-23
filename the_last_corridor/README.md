# 👁️ THE LAST CORRIDOR — Jogo de Terror Psicológico com Desktop Simulado

**THE LAST CORRIDOR** é uma experiência de terror psicológico para Windows dividida em duas fases conectadas narrativamente:
1. **O Labirinto:** Um ambiente claustrofóbico em visão superior, iluminado apenas pela lanterna instável do jogador. Conforme os corredores são explorados, silhuetas e imagens macabras piscam repentinamente na tela (flashes curtos de 100 a 250ms). Ao alcançar a saída, um jumpscare violento interrompe o movimento com tremores e distorções sonoras.
2. **O Computador Antigo Simulado (ARCHIVE-09):** O labirinto desaparece e a tela inicializa um computador retrô fictício com referências aos sistemas dos anos 1990/2000. O jogador precisa explorar pastas, ler documentos no bloco de notas, esquivar de pastas perigosas (que disparam jumpscares próprios) e decifrar um código secreto.

O objetivo final é atender à mensagem obrigatória exibida no desktop:
> **"EXISTE UM ARQUIVO NO SEU COMPUTADOR, O ENCONTRE E ESCREVA O CODIGO AQUI"**

---

## 🔒 Segurança e Privacidade
- O jogo funciona **100% offline** e de forma local.
- O sistema de arquivos investigado é **totalmente fictício e em memória**. O jogo **NUNCA** acessa, vasculha, move ou altera arquivos pessoais reais do seu computador Windows.
- Não solicita privilégios de administrador.

---

## ⚙️ Pré-requisitos e Instalação

### Dependências
- **Python 3.12+** (ou versão compatível)
- **Pygame 2.6+**
- **NumPy**
- **PyInstaller** (para compilação em executável)

Para instalar as dependências:
```bash
pip install -r the_last_corridor/requirements.txt
```

---

## 🎮 Como Jogar

### 1. Em Modo Desenvolvimento (Python):
Execute o arquivo principal:
```bash
python the_last_corridor/main.py
```
*(ou dê dois cliques no arquivo `jogar_the_last_corridor.bat`)*

### 2. Executável Windows (.exe):
Se compilado com PyInstaller, execute:
```bash
dist/TheLastCorridor/TheLastCorridor.exe
```

---

## 🕹️ Controles

### No Labirinto:
- `W`, `A`, `S`, `D` ou `Setas do Teclado`: Movimentação fluida com deslizamento em paredes.
- `ESC`: Pausa e salva o progresso, retornando ao Menu Principal.
- `F11`: Alternar entre Janela e Tela Cheia.

### No Computador Simulado:
- `Mouse`: Mover o cursor retrô, arrastar janelas pela barra de título.
- `Clique Duplo`: Abrir pastas no Explorador de Arquivos ou abrir arquivos `.txt` no Bloco de Notas.
- `Teclado`: Digitar o código secreto no campo de texto da janela de verificação.
- `Botão Minimizar [_]`: Oculta a janela de verificação para visualizar o desktop. O ícone permanece acessível na barra de tarefas.

---

## 🛠️ Painel de Personalização do Criador

Acessível diretamente pelo menu em **PERSONALIZAR JOGO**, sem necessidade de editar código:

1. **Aba LABIRINTO**:
   - Tamanho do grid (15x15, 19x19, 25x25).
   - Velocidade do jogador e raio de alcance da lanterna.
2. **Aba APARIÇÕES**:
   - Duração dos flashes (120ms, 180ms, 250ms).
   - Intervalo mínimo de segurança entre sustos (evita sobreposição).
   - Probabilidade e frequência.
3. **Aba JUMPSCARE**:
   - Duração do susto principal.
   - Ativação de tremor de tela, zoom e flashes estroboscópicos.
4. **Aba DESKTOP & PASTAS**:
   - Nome fictício da máquina (ex: `ARCHIVE-09`, `TERMINAL_1998`).
   - Marcar pastas como **SEGURA** ou **PERIGOSA** (aciona jumpscare ao abrir).
5. **Aba CÓDIGO & FINAL**:
   - Alterar o código secreto (padrão: `OMEGA-7341`).
   - Caminho do documento onde a chave fica escondida.
6. **Aba PERFIS**:
   - Salvar e carregar perfis em formato JSON.
   - Restaurar configurações padrão com um clique.

---

## 🧪 Testes Automatizados

O projeto inclui suíte completa com **21 testes unitários e de integração**:
```bash
python -m unittest discover -s the_last_corridor/tests
```

Itens testados:
- Geração e integridade do labirinto (caminho garantido entre início e saída).
- Detecção e resolução de colisões com deslizamento.
- Sistema de aparições relâmpago e controle de frequência.
- Ciclo de vida e temporização do jumpscare final.
- Árvore de diretórios do sistema de arquivos virtual.
- Validação exata da frase obrigatória e do código secreto.
- Serialização e persistência de perfis JSON.

---

## 📦 Como Gerar o Executável (.exe)

Para compilar novamente o executável com PyInstaller:
```powershell
python -m PyInstaller --noconfirm --onedir --windowed --name "TheLastCorridor" --add-data "the_last_corridor/assets;assets" the_last_corridor/main.py
```
O executável final e seus recursos serão gerados na pasta:
`dist/TheLastCorridor/TheLastCorridor.exe`
