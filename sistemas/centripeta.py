
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
 
# ---------------------------------------------------------------------------
# FÍSICA (separada da interface)
# ---------------------------------------------------------------------------
 
def calcular_grandezas(R, v, m):
    """Calcula as grandezas do MCU a partir de R, v e m."""
    # Velocidade angular: no MCU o corpo percorre o arco v·t, e arco = R·θ,
    # logo θ = (v/R)·t, ou seja, ω = v / R.
    omega = v / R
 
    # Período: tempo de uma volta completa (2π rad) com velocidade angular ω.
    periodo = 2 * np.pi / omega
 
    # Aceleração centrípeta: a direção da velocidade muda o tempo todo, então
    # há aceleração apontando para o centro, de módulo a_c = v² / R = ω²·R.
    a_c = v ** 2 / R
 
    # 2ª Lei de Newton na direção radial: ΣF = m·a  →  Fc = m·v² / R = m·ω²·R.
    # A força centrípeta não é uma força nova: é a resultante (aqui, a tração
    # do fio) que aponta para o centro.
    f_c = m * a_c
 
    return omega, periodo, a_c, f_c
 
 
def calcular_posicao(R, omega, t):
    """Posição no círculo: x(t) = R·cos(ωt) e y(t) = R·sen(ωt).
    Aceita t escalar ou vetor NumPy."""
    x = R * np.cos(omega * t)
    y = R * np.sin(omega * t)
    return x, y
 
 
# ---------------------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------------------
 
def criar_figura(R, omega, periodo):
    """Cria a figura uma única vez, com os elementos fixos (trajetória,
    centro, limites) e os elementos que se movem (fio, corpo, setas).
    Reaproveitar a figura entre os quadros deixa a animação bem mais leve."""
    fig, ax = plt.subplots(figsize=(4, 4))
 
    # Trajetória: uma volta completa avaliada sobre um vetor de tempo.
    t_volta = np.linspace(0, periodo, 200)
    xs, ys = calcular_posicao(R, omega, t_volta)
    ax.plot(xs, ys, "--", color="lightgray")
    ax.plot(0, 0, "k+", markersize=10)
 
    # Elementos que mudam a cada instante (posições definidas em atualizar_quadro).
    fio, = ax.plot([], [], color="gray", lw=1.5)
    corpo, = ax.plot([], [], "o", color="steelblue", markersize=12)
    seta_fc = ax.annotate("", xy=(0, 0), xytext=(0, 0),
                          arrowprops=dict(arrowstyle="-|>", color="crimson", lw=2))
    seta_v = ax.annotate("", xy=(0, 0), xytext=(0, 0),
                         arrowprops=dict(arrowstyle="-|>", color="seagreen", lw=2))
 
    # Legenda com linhas "fantasma" só para mostrar as cores das setas.
    ax.plot([], [], color="crimson", lw=2, label="Força centrípeta Fc")
    ax.plot([], [], color="seagreen", lw=2, label="Velocidade v")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=8)
 
    limite = 1.4 * R
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.grid(True, alpha=0.3)
    titulo = ax.set_title("")
 
    elementos = {"fio": fio, "corpo": corpo, "seta_fc": seta_fc,
                 "seta_v": seta_v, "titulo": titulo}
    return fig, elementos
 
 
def atualizar_quadro(elementos, R, omega, t):
    """Move o corpo, o fio e as setas para o instante t."""
    x, y = calcular_posicao(R, omega, t)
    ux, uy = x / R, y / R   # vetor unitário radial (do centro para o corpo)
    comprimento = 0.35 * R  # comprimento fixo das setas, só indica a direção
 
    elementos["fio"].set_data([0, x], [0, y])
    elementos["corpo"].set_data([x], [y])
 
    # Força centrípeta: aponta para o centro (sentido oposto ao radial).
    elementos["seta_fc"].set_position((x, y))
    elementos["seta_fc"].xy = (x - comprimento * ux, y - comprimento * uy)
 
    # Velocidade: tangente ao círculo, perpendicular ao raio.
    elementos["seta_v"].set_position((x, y))
    elementos["seta_v"].xy = (x - comprimento * uy, y + comprimento * ux)
 
    elementos["titulo"].set_text(f"t = {t:.2f} s")
 
 
# Página HTML da animação. Roda inteira no NAVEGADOR (canvas + JavaScript),
# por isso não depende da velocidade da conexão com o servidor. Os valores R,
# ω e T são calculados em Python e inseridos nos marcadores __R__, __OMEGA__
# e __T__; o JavaScript só desenha.
_HTML_ANIMACAO = """
<div style="font-family: sans-serif; text-align: center;">
  <canvas id="c" width="360" height="400"></canvas>
</div>
<script>
  const R = __R__, omega = __OMEGA__, T = __T__;
  const canvas = document.getElementById("c");
  const ctx = canvas.getContext("2d");
  const cx = 180, cy = 190;             // origem (0, 0) no canvas
  const escala = 165 / (1.4 * R);       // pixels por metro (mesmos limites do gráfico: ±1.4R)
 
  // Converte (x, y) em metros para pixels (o eixo y do canvas cresce para baixo).
  const px = (x) => cx + x * escala;
  const py = (y) => cy - y * escala;
 
  function seta(x0, y0, dx, dy, cor) {   // seta em pixels, de (x0, y0) na direção (dx, dy)
    const c = 0.35 * R * escala;         // comprimento fixo: só indica a direção
    const x1 = x0 + dx * c, y1 = y0 + dy * c;
    const ang = Math.atan2(dy, dx);
    ctx.strokeStyle = cor; ctx.fillStyle = cor; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x1 - 9 * Math.cos(ang - 0.4), y1 - 9 * Math.sin(ang - 0.4));
    ctx.lineTo(x1 - 9 * Math.cos(ang + 0.4), y1 - 9 * Math.sin(ang + 0.4));
    ctx.closePath(); ctx.fill();
  }
 
  function desenhar(t) {
    ctx.clearRect(0, 0, 360, 400);
    ctx.strokeStyle = "#999"; ctx.lineWidth = 1;
    ctx.strokeRect(10, 25, 340, 340);                      // moldura do gráfico
 
    ctx.setLineDash([6, 5]); ctx.strokeStyle = "#ccc";     // trajetória
    ctx.beginPath(); ctx.arc(cx, cy, R * escala, 0, 2 * Math.PI); ctx.stroke();
    ctx.setLineDash([]);
 
    // MESMAS equações do MCU usadas em Python (calcular_posicao):
    // x(t) = R·cos(ωt) e y(t) = R·sen(ωt)
    const x = R * Math.cos(omega * t), y = R * Math.sin(omega * t);
    const ux = Math.cos(omega * t), uy = Math.sin(omega * t);  // unitário radial
 
    ctx.strokeStyle = "gray"; ctx.lineWidth = 1.5;         // fio
    ctx.beginPath(); ctx.moveTo(px(0), py(0)); ctx.lineTo(px(x), py(y)); ctx.stroke();
 
    seta(px(x), py(y), -ux, uy, "crimson");                // Fc: aponta para o centro
    seta(px(x), py(y), -uy, -ux, "seagreen");              // v: tangente ao círculo
 
    ctx.fillStyle = "steelblue";                           // corpo
    ctx.beginPath(); ctx.arc(px(x), py(y), 8, 0, 2 * Math.PI); ctx.fill();
 
    ctx.fillStyle = "black"; ctx.font = "14px sans-serif"; ctx.textAlign = "center";
    ctx.fillText("t = " + t.toFixed(2) + " s", cx, 18);
    ctx.fillStyle = "crimson"; ctx.fillText("— Força centrípeta Fc", 105, 392);
    ctx.fillStyle = "seagreen"; ctx.fillText("— Velocidade v", 280, 392);
  }
 
  // Animação em tempo real: a cada quadro, t é o tempo REALMENTE decorrido
  // (relógio do navegador). Uma volta dura exatamente T segundos.
  let inicioAnim, idAnim;
  function passo(agora) {
    if (inicioAnim === undefined) inicioAnim = agora;
    const t = Math.min((agora - inicioAnim) / 1000, T);
    desenhar(t);
    if (t < T) idAnim = requestAnimationFrame(passo);
  }
  function iniciar() {
    cancelAnimationFrame(idAnim);
    inicioAnim = undefined;
    idAnim = requestAnimationFrame(passo);
  }
  if (__INICIAR__) {
    iniciar();
  } else {
    desenhar(0);
  }
</script>
"""
 
 
def gerar_html_animacao(R, omega, periodo, iniciar=False):
    """Monta o HTML com os parâmetros e define se a volta deve iniciar."""
    return (_HTML_ANIMACAO
            .replace("__R__", repr(float(R)))
            .replace("__OMEGA__", repr(float(omega)))
            .replace("__T__", repr(float(periodo)))
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
    """Tela do sistema: controles | gráfico | valores calculados."""
    st.subheader("Força Centrípeta — Movimento Circular Uniforme")
    st.write(
        "Uma massa presa a um fio gira em um círculo horizontal com velocidade "
        "tangencial constante. Ajuste os parâmetros e veja a força centrípeta."
    )
 
    col_controles, col_grafico, col_valores = st.columns([1, 1.3, 1])
 
    with col_controles:
        R = st.slider("Raio R (m)", 0.5, 10.0, 3.0, 0.1)
        v = st.slider("Velocidade tangencial v (m/s)", 0.5, 20.0, 5.0, 0.1)
        m = st.slider("Massa m (kg)", 0.1, 10.0, 1.0, 0.1)
        iniciar_volta = st.button("▶ Iniciar volta")

    omega, periodo, a_c, f_c = calcular_grandezas(R, v, m)

    with col_grafico:
        # Alterar qualquer slider faz o Streamlit reconstruir este HTML com os
        # parâmetros atualizados
        # A animação só começa quando o usuário clica no botão.
        exibir_html(gerar_html_animacao(R, omega, periodo, iniciar=iniciar_volta), 440)
 
    # Grandezas calculadas, atualizadas a cada mudança nos sliders.
    with col_valores:
        st.metric("Força centrípeta Fc", f"{f_c:.2f} N")
        st.metric("Velocidade angular ω", f"{omega:.2f} rad/s")
        st.metric("Aceleração centrípeta", f"{a_c:.2f} m/s²")
        st.metric("Período T (tempo de uma volta)", f"{periodo:.2f} s")
 
    with st.expander("Equações utilizadas"):
        st.latex(r"\omega = \frac{v}{R}")
        st.latex(r"x(t) = R\cos(\omega t) \qquad y(t) = R\sin(\omega t)")
        st.latex(r"F_c = \frac{m v^2}{R} = m \omega^2 R")
        st.latex(r"T = \frac{2\pi}{\omega}")
 