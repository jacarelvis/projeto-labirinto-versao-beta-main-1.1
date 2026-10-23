# 🎮 Labirinto Aventura

Um jogo de labirinto moderno e interativo com geração procedural garantida (algoritmo DFS / Recursive Backtracker) e busca de caminho para dicas (BFS).

Disponível em duas versões completas:
1. **Versão Web (HTML5 Canvas + JavaScript + CSS)**: Interface moderna em tons neon, efeitos sonoros sintetizados via Web Audio API, modo lanterna (*fog of war*), suporte a controles virtuais touch e teclado.
2. **Versão Desktop em Python (Tkinter)**: Janela nativa leve usando apenas a biblioteca padrão do Python, sem necessidade de instalar dependências extras (`pip`).

---

## 🚀 Como Jogar

### Opção 1: Pelo Inicializador Rápido (Windows)
Basta dar dois cliques no arquivo:
- `jogar.bat` e escolher entre a versão Web ou Python.

### Opção 2: Versão Web no Navegador (Recomendada)
- Dê dois cliques diretamente no arquivo [`index.html`](index.html).
- O jogo abrirá no seu navegador padrão (Chrome, Edge, Firefox, etc.).

### Opção 3: Versão Desktop Python
Abra o terminal na pasta do projeto e execute:
```bash
python labirinto.py
```

---

## 🎯 Regras e Objetivo
- O jogador começa no canto superior esquerdo e deve encontrar o caminho até a saída 🚪.
- Colete as gemas 💎 espalhadas pelos becos sem saída para conseguir a pontuação máxima!
- Tente escapar no menor tempo ⏱️ e com o menor número de passos 👣.

---

## 🕹️ Controles

| Ação | Teclado | Celular / Mouse |
|---|---|---|
| Mover para Cima | `W` ou `Seta para Cima (↑)` | Botão ▲ ou Deslizar para cima |
| Mover para Baixo | `S` ou `Seta para Baixo (↓)` | Botão ▼ ou Deslizar para baixo |
| Mover para a Esquerda | `A` ou `Seta para a Esquerda (←)` | Botão ◀ ou Deslizar para esquerda |
| Mover para a Direita | `D` ou `Seta para a Direita (→)` | Botão ▶ ou Deslizar para direita |

---

## ✨ Recursos Implementados

- **Geração Procedural Perfeita**: Cada labirinto gerado é único e 100% resolvível.
- **3 Níveis de Dificuldade**:
  - *Fácil*: 11x11
  - *Médio*: 21x21
  - *Difícil*: 31x31
- **Sistema de Dicas (BFS)**: Se ficar preso, use o botão de dica para revelar o menor caminho até a saída.
- **Modo Lanterna (Fog of War)**: Oculte o mapa e explore no escuro com um raio de visão limitado ao redor do personagem!
- **Efeitos Sonoros**: Sons de passos, colisão com paredes, coleta de itens e fanfarra de vitória sem necessidade de arquivos externos de áudio.
- **Sistema de Recordes**: Gravação do menor tempo por dificuldade no `localStorage`.
