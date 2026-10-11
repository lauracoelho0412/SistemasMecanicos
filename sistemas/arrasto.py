"""Sistema 3.3 — Força de arrasto."""

import json

import numpy as np
import streamlit as st


# ---------------------------------------------------------------------------
# FÍSICA (separada da interface)
# ---------------------------------------------------------------------------

GRAVIDADE = 9.81


def calcular_grandezas(massa, coeficiente_linear, coeficiente_quadratico, gravidade=GRAVIDADE):
    """Calcula velocidades terminais e constante de tempo para os dois modelos."""
    velocidade_terminal_linear = massa * gravidade / coeficiente_linear
    constante_tempo_linear = massa / coeficiente_linear
    velocidade_terminal_quadratica = np.sqrt(massa * gravidade / coeficiente_quadratico)
    return (
        velocidade_terminal_linear,
        constante_tempo_linear,
        velocidade_terminal_quadratica,
    )


def velocidade_linear(
    tempo: np.ndarray, massa: float, coeficiente: float, gravidade: float = GRAVIDADE
) -> np.ndarray:
    """Velocidade de queda com arrasto linear, partindo do repouso."""
    velocidade_terminal = massa * gravidade / coeficiente
    constante_tempo = massa / coeficiente
    return velocidade_terminal * (1 - np.exp(-tempo / constante_tempo))


def velocidade_quadratica(
    tempo: np.ndarray, massa: float, coeficiente: float, gravidade: float = GRAVIDADE
) -> np.ndarray:
    """Velocidade de queda com arrasto quadrático, partindo do repouso."""
    velocidade_terminal = np.sqrt(massa * gravidade / coeficiente)
    return velocidade_terminal * np.tanh(gravidade * tempo / velocidade_terminal)


# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------

# Página HTML do gráfico. Roda inteira no NAVEGADOR (canvas + JavaScript), por
# isso não depende da velocidade da conexão com o servidor. As curvas v(t) são
# calculadas em Python (funções acima, sobre um vetor de tempo) e enviadas no
# marcador __DADOS__; o JavaScript só desenha e move o marcador.
_HTML_GRAFICO = """
<style>
  html, body { margin: 0; padding: 0; background: transparent; }
  canvas { display: block; }
</style>
<canvas id="c" height="380"></canvas>
<script>
  const D = __DADOS__;
  const canvas = document.getElementById("c");
  const ctx = canvas.getContext("2d");
  const ALTURA = 380;
  const M = { esq: 62, dir: 18, topo: 46, base: 52 };   // margens do gráfico (px)
  const COR = {
    fundo: "#ffffff", painel: "#ffffff", grade: "#9ca3af", texto: "#31333F",
    titulo: "#31333F", linear: "#0284c7", quad: "#9333ea", livre: "#e69f00"
  };

  const tMax = D.tempo[D.tempo.length - 1];
  const yMax = 1.05 * Math.max(...D.vl, ...D.vq, ...D.vlivre);
  let W = 640, H = ALTURA, tAtual = null;

  // A largura acompanha a coluna do Streamlit.
  function ajustar() {
    W = Math.max(320, window.innerWidth);
    canvas.width = W;
    canvas.height = H;
  }

  // Converte tempo (s) e velocidade (m/s) em pixels (o eixo y do canvas cresce para baixo).
  const px = (t) => M.esq + (t / tMax) * (W - M.esq - M.dir);
  const py = (v) => H - M.base - (v / yMax) * (H - M.topo - M.base);

  // Valor da curva em um instante t qualquer (interpolação entre dois pontos do vetor).
  function valorEm(arr, t) {
    const f = (t / tMax) * (arr.length - 1);
    const i = Math.min(Math.floor(f), arr.length - 2);
    const r = f - i;
    return arr[i] * (1 - r) + arr[i + 1] * r;
  }

  // Passo "redondo" (1, 2, 5 x 10^k) para as marcas dos eixos.
  function passoBonito(maximo) {
    const bruto = maximo / 5;
    const p = Math.pow(10, Math.floor(Math.log10(bruto)));
    const f = bruto / p;
    return (f < 1.5 ? 1 : f < 3.5 ? 2 : f < 7.5 ? 5 : 10) * p;
  }
  const casas = (passo) => (passo >= 1 ? 0 : Math.ceil(-Math.log10(passo) - 1e-9));

  function eixos() {
    const larguraPlot = W - M.esq - M.dir, alturaPlot = H - M.topo - M.base;
    ctx.fillStyle = COR.painel;
    ctx.fillRect(M.esq, M.topo, larguraPlot, alturaPlot);

    ctx.font = "12px sans-serif";
    ctx.fillStyle = COR.texto; ctx.strokeStyle = COR.grade; ctx.lineWidth = 1;

    const pT = passoBonito(tMax), pV = passoBonito(yMax);
    ctx.textAlign = "center"; ctx.textBaseline = "top";
    for (let i = 0; i * pT <= tMax + 1e-9; i++) {
      const x = px(i * pT);
      ctx.globalAlpha = 0.3;
      ctx.beginPath(); ctx.moveTo(x, M.topo); ctx.lineTo(x, H - M.base); ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.fillText((i * pT).toFixed(casas(pT)), x, H - M.base + 6);
    }
    ctx.textAlign = "right"; ctx.textBaseline = "middle";
    for (let i = 0; i * pV <= yMax + 1e-9; i++) {
      const y = py(i * pV);
      ctx.globalAlpha = 0.3;
      ctx.beginPath(); ctx.moveTo(M.esq, y); ctx.lineTo(W - M.dir, y); ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.fillText((i * pV).toFixed(casas(pV)), M.esq - 8, y);
    }

    // Bordas esquerda e inferior (as outras ficam sem linha, como no estilo original).
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(M.esq, M.topo); ctx.lineTo(M.esq, H - M.base); ctx.lineTo(W - M.dir, H - M.base);
    ctx.stroke();

    ctx.fillStyle = COR.texto; ctx.textAlign = "center"; ctx.textBaseline = "alphabetic";
    ctx.fillText("Tempo (s)", M.esq + larguraPlot / 2, H - 10);
    ctx.save();
    ctx.translate(16, M.topo + alturaPlot / 2); ctx.rotate(-Math.PI / 2);
    ctx.fillText("Velocidade (m/s)", 0, 0);
    ctx.restore();

    ctx.fillStyle = COR.titulo; ctx.font = "bold 15px sans-serif"; ctx.textAlign = "left";
    ctx.fillText("Velocidade de queda", M.esq, 26);
  }

  function curva(arr, cor, largura, tracejado) {
    ctx.strokeStyle = cor; ctx.lineWidth = largura;
    ctx.setLineDash(tracejado ? [7, 5] : []);
    ctx.beginPath();
    for (let i = 0; i < arr.length; i++) {
      const x = px(D.tempo[i]), y = py(arr[i]);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
  }

  function legenda() {
    const itens = [["Arrasto linear", COR.linear, false],
                   ["Arrasto quadrático", COR.quad, false],
                   ["Sem arrasto: queda livre", COR.livre, true]];
    const x0 = M.esq + 12, y0 = M.topo + 12, larg = 212, alt = 12 + itens.length * 22;
    ctx.fillStyle = COR.painel; ctx.strokeStyle = "#d1d5db"; ctx.lineWidth = 1;
    ctx.fillRect(x0, y0, larg, alt); ctx.strokeRect(x0, y0, larg, alt);
    ctx.font = "12px sans-serif"; ctx.textAlign = "left"; ctx.textBaseline = "middle";
    itens.forEach(([nome, cor, tracejado], i) => {
      const y = y0 + 17 + i * 22;
      ctx.strokeStyle = cor; ctx.lineWidth = 2.5;
      ctx.setLineDash(tracejado ? [6, 4] : []);
      ctx.beginPath(); ctx.moveTo(x0 + 10, y); ctx.lineTo(x0 + 38, y); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = COR.texto; ctx.fillText(nome, x0 + 46, y);
    });
  }

  // Marcador do modelo escolhido + caixa com t, v e a força de arrasto.
  function marcador(t) {
    const arr = D.linear ? D.vl : D.vq;
    const cor = D.linear ? COR.linear : COR.quad;
    const v = valorEm(arr, t);
    // Fd = b·v (arrasto linear)  ou  Fd = c·v² (arrasto quadrático)
    const fd = D.linear ? D.b * v : D.c * v * v;
    const x = px(t), y = py(v);

    ctx.globalAlpha = 0.4; ctx.strokeStyle = COR.titulo; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(x, M.topo); ctx.lineTo(x, H - M.base); ctx.stroke();
    ctx.globalAlpha = 1;

    ctx.fillStyle = cor; ctx.strokeStyle = "#ffffff"; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(x, y, 6, 0, 2 * Math.PI); ctx.fill(); ctx.stroke();

    const linhas = ["t = " + t.toFixed(1) + " s",
                    "v = " + v.toFixed(2) + " m/s",
                    "Fd = " + fd.toFixed(2) + " N / mg = " + D.peso.toFixed(2) + " N"];
    ctx.font = "12px sans-serif";
    const larg = Math.max(...linhas.map((l) => ctx.measureText(l).width)) + 16;
    const alt = linhas.length * 17 + 10;
    const bx = Math.min(x + 12, W - M.dir - larg);   // não passa da borda direita
    const by = Math.max(y - 12 - alt, M.topo + 4);   // não sobe além do gráfico
    ctx.fillStyle = COR.fundo; ctx.strokeStyle = cor; ctx.lineWidth = 1.2;
    ctx.fillRect(bx, by, larg, alt); ctx.strokeRect(bx, by, larg, alt);
    ctx.fillStyle = COR.titulo; ctx.textAlign = "left"; ctx.textBaseline = "top";
    linhas.forEach((l, i) => ctx.fillText(l, bx + 8, by + 6 + i * 17));
  }

  function desenhar(t) {
    ctx.fillStyle = COR.fundo;
    ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = "#e6e9ef"; ctx.lineWidth = 1;
    ctx.strokeRect(0.5, 0.5, W - 1, H - 1);                // borda fina do cartão
    eixos();
    curva(D.vl, COR.linear, 2.8, false);
    curva(D.vq, COR.quad, 2.8, false);
    curva(D.vlivre, COR.livre, 2, true);
    legenda();
    if (t !== null) marcador(t);
  }

  // Animação em tempo real: a cada quadro, t é o tempo REALMENTE decorrido
  // (relógio do navegador). O percurso de 0 até o tempo máximo dura exatamente
  // esse número de segundos.
  let inicioAnim, idAnim;
  function passo(agora) {
    if (inicioAnim === undefined) inicioAnim = agora;
    tAtual = Math.min((agora - inicioAnim) / 1000, tMax);
    desenhar(tAtual);
    if (tAtual < tMax) idAnim = requestAnimationFrame(passo);
  }
  function iniciar() {
    cancelAnimationFrame(idAnim);
    inicioAnim = undefined;
    idAnim = requestAnimationFrame(passo);
  }

  window.addEventListener("resize", () => { ajustar(); desenhar(tAtual); });
  ajustar();
  if (__INICIAR__) {
    iniciar();
  } else {
    desenhar(null);
  }
</script>
"""


def gerar_html_grafico(tempo, vel_linear, vel_quadratica, vel_livre,
                       modelo, b, c, peso, iniciar=False):
    """Monta o HTML do gráfico com as curvas calculadas em Python e define
    se a animação deve começar."""
    dados = {
        "tempo": np.round(tempo, 4).tolist(),
        "vl": np.round(vel_linear, 4).tolist(),
        "vq": np.round(vel_quadratica, 4).tolist(),
        "vlivre": np.round(vel_livre, 4).tolist(),
        "linear": modelo == "linear",   # modelo cujo marcador será animado
        "b": float(b),
        "c": float(c),
        "peso": float(peso),
    }
    return (_HTML_GRAFICO
            .replace("__DADOS__", json.dumps(dados))
            .replace("__INICIAR__", "true" if iniciar else "false"))


def exibir_html(html, altura):
    """Mostra uma página HTML dentro do app. Usa st.iframe (versões novas do
    Streamlit) e, se não existir, o antigo components.html."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=altura)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=altura)


def renderizar():
    st.subheader("Força de arrasto")
    st.caption(
        "A força de arrasto se opõe à queda. A curva tracejada representa "
        "a queda livre, sem resistência do ar."
    )

    col_controles, col_visualizacao, col_valores = st.columns([1.1, 2.4, 1.1])
    with col_controles:
        massa = st.slider("Massa (kg)", 0.1, 10.0, 1.0, 0.1)
        coeficiente_linear = st.slider(
            "Coeficiente linear b (kg/s)", 0.1, 5.0, 0.5, 0.1
        )
        coeficiente_quadratico = st.slider(
            "Coeficiente quadrático c (kg/m)", 0.1, 5.0, 0.5, 0.1
        )
        duracao = st.slider("Tempo máximo (s)", 0.1, 10.0, 10.0, 0.5)
        modelo = st.radio(
            "Animação",
            ("linear", "quadrático"),
            format_func=lambda valor: f"Arrasto {valor}",
        )
        iniciar_animacao = st.button("▶ Iniciar animação")

    vt_linear, _, vt_quadratico = calcular_grandezas(
        massa, coeficiente_linear, coeficiente_quadratico
    )
    # Fórmulas fechadas avaliadas direto sobre um vetor de tempo (sem integração).
    tempo = np.linspace(0, duracao, 500)
    velocidade_l = velocidade_linear(tempo, massa, coeficiente_linear)
    velocidade_q = velocidade_quadratica(tempo, massa, coeficiente_quadratico)
    velocidade_livre = GRAVIDADE * tempo

    with col_visualizacao:
        # Alterar qualquer controle reconstrói este HTML com os parâmetros
        # atualizados. A animação só começa quando o botão é clicado.
        exibir_html(
            gerar_html_grafico(
                tempo, velocidade_l, velocidade_q, velocidade_livre,
                modelo, coeficiente_linear, coeficiente_quadratico,
                massa * GRAVIDADE, iniciar=iniciar_animacao,
            ),
            400,
        )

    with col_valores:
        st.markdown("#### Valores")
        st.metric("Terminal · linear", f"{vt_linear:.2f} m/s")
        st.caption(
            f"Valor no fim do gráfico (t = {duracao:g} s): {velocidade_l[-1]:.2f} m/s"
        )
        st.metric("Terminal · quadrático", f"{vt_quadratico:.2f} m/s")
        st.caption(
            f"Valor no fim do gráfico (t = {duracao:g} s): {velocidade_q[-1]:.2f} m/s"
        )
        st.metric("Queda livre ao final", f"{velocidade_livre[-1]:.2f} m/s")
        st.caption("Durante a animação, o marcador mostra t, v e a força de arrasto.")

    with st.expander("Equações utilizadas"):
        st.latex(r"\text{Arrasto linear:} \qquad F_d = -b v")
        st.latex(r"v_{\text{terminal}} = \frac{mg}{b}")
        st.latex(r"\tau = \frac{m}{b}")
        st.latex(r"v(t) = v_{\text{terminal}} \left(1 - e^{-\frac{t}{\tau}}\right)")
        st.latex(
            r"x(t) = v_{\text{terminal}}\left[t-\tau\left(1-e^{-\frac{t}{\tau}}\right)\right]"
        )
        st.latex(r"\text{Arrasto quadrático:} \qquad F_d = -c v|v|")
        st.latex(r"v_{\text{terminal}} = \sqrt{\frac{mg}{c}}")
        st.latex(r"v(t) = v_{\text{terminal}} \tanh\left(\frac{g t}{v_{\text{terminal}}}\right)")
        st.latex(
            r"y(t) = \frac{v_{\text{terminal}}^2}{g} "
            r"\ln\left(\cosh\left(\frac{g t}{v_{\text{terminal}}}\right)\right)"
        )