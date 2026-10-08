# Leis de Newton — Simulador Interativo

Atividade ADO 2 de Física (Mecânica e Física Moderna) — aplicação web em
Python que simula sistemas clássicos da Mecânica a partir da Segunda Lei de
Newton, usando apenas fórmulas fechadas (sem integração numérica).

🔗 **Link da aplicação:** _(colar aqui o link do Streamlit Cloud depois de publicar)_

## Sistemas

- Plano Inclinado com Atrito e Tração
- Força Centrípeta
- Força de Arrasto

### Força centrípeta

Uma massa presa a um fio gira em um círculo horizontal com velocidade
tangencial constante (movimento circular uniforme).

- Sliders para raio R, velocidade tangencial v e massa m
- Slider de posição na volta e botão para animar uma volta completa
- Gráfico com a trajetória, o fio e os vetores de força centrípeta e velocidade
- Valores calculados em tempo real: força centrípeta, velocidade angular,
  aceleração centrípeta e período
- Painel com as equações utilizadas

Equações: `ω = v/R`, `x(t) = R·cos(ωt)`, `y(t) = R·sen(ωt)`,
`Fc = m·v²/R = m·ω²·R`.

## Requisitos

- Python 3.10+
- Bibliotecas: `streamlit`, `numpy`, `matplotlib` (listadas em `requirements.txt`)

## Como executar localmente

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O navegador abre automaticamente em `http://localhost:8501`.

Se o `pip` não estiver disponível na sua instalação do Python:

```bash
python -m ensurepip --upgrade
```

## Como publicar (link clicável)

1. Suba este projeto para um repositório no GitHub, com o `app.py` e o
   `requirements.txt` na raiz.
2. Acesse [share.streamlit.io](https://share.streamlit.io) e entre com a conta
   do GitHub.
3. Clique em **Create app**, escolha o repositório e a branch, e informe
   `app.py` como arquivo principal.
4. Clique em **Deploy** e copie o link gerado para o topo deste README.

Observação: apps gratuitos entram em "repouso" depois de um tempo sem uso, e o
primeiro acesso pode levar alguns segundos para reativá-lo.

## Estrutura do projeto

```
├── app.py                      # menu
├── requirements.txt            # dependências
└── sistemas/
    ├── centripeta.py          
    ├── plano_inclinado.py      
    └── arrasto.py              
```

Cada sistema é um módulo com a função `renderizar()`, que o `app.py` chama
conforme o botão escolhido. Em cada módulo, a parte de física
(`calcular_*`) fica separada da parte de interface.

## Autores

- Laura Coelho
- Pedro Zeferino Bittencourt
- Paulo Eduardo

## Licença

Uso acadêmico.
