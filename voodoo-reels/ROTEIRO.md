# Reels "Vudú" — Sua Vez Locação de Jogos

Formato: vertical 9:16 (1080×1920), **68 segundos**, stop motion de recortes
(fotos reais das peças do jogo animadas quadro a quadro, 12 poses por segundo).

Arquivos gerados (`out/`):

| arquivo | para quê |
|---|---|
| `vudu_preview.mp4` | prévia com legendas + música + efeitos |
| `vudu_limpo.mp4` | mesmo vídeo **sem legendas**: é nele que você grava a narração |
| `trilha.wav` | só a música + efeitos, para editar à parte |
| `../legendas.srt` | legendas no tempo do roteiro (importa no CapCut/Premiere) |

---

## Roteiro de narração

Tom: animado e cúmplice, como quem conta uma travessura para um amigo. Sorria
enquanto fala (dá para ouvir). Nas reticências, faça uma pausinha dramática.

| tempo | cena (o que aparece) | fala |
|---|---|---|
| 0:00 – 0:05 | **GANCHO.** O Vuduzinho entra pulando, caveiras chegam, ele leva um "zap". | "E se você pudesse **amaldiçoar** seus amigos... e ainda ganhar **pontos** com isso?" |
| 0:05 – 0:11 | A caixa do Vudú cai na mesa, o logo aparece, o boneco espia. | "Esse é o **Vudú**: o jogo em que você é um feiticeiro perverso... e a sua galera vira vítima." |
| 0:11 – 0:22 | Os 5 dados rolam; 3 são guardados, 1 vai embora, 1 é rolado de novo. | "Na sua vez, você rola **cinco dados** de ingredientes. Não gostou? Guarda os que servem e rola de novo... mas cada nova rolagem **custa um dado**." |
| 0:22 – 0:30 | A carta vira (Kapoera), os dados pulam para dentro dela, a maldição acerta o boneco. | "Juntou os ingredientes da carta? **Lança a maldição** em alguém da mesa e marca pontos." |
| 0:30 – 0:37 | Carta Kapoera + boneco flutuando sem tocar o chão. | "E aí começa o caos! Na **Kapoera**, a vítima não pode encostar os pés no chão..." |
| 0:37 – 0:45 | Carta Tutakobraço + boneco com os braços esticados, tremendo. | "Na **Tutakobraço**, tem que ficar com os braços esticados... e tem maldição **muito pior**." |
| 0:45 – 0:52 | O boneco relaxa, carimbo "ESQUECEU!"; a caveira vermelha avança no tabuleiro. | "Esqueceu da maldição? Quem lançou ganha **ainda mais pontos**." |
| 0:52 – 0:58 | A caveira chega no 11, confete, "VENCEU!". | "Quem chegar primeiro nos **onze pontos** vence. De duas a oito pessoas, em uns trinta minutos." |
| 0:58 – 1:08 | Logo da Sua Vez, "Alugue o Vudú", "Link na bio", pergunta para comentar. | "Quer amaldiçoar sua galera no fim de semana? **Aluga o Vudú na Sua Vez**: link na bio! E comenta aqui: qual maldição você jogaria no seu melhor amigo?" |

Texto corrido (para ler de uma vez):

> E se você pudesse amaldiçoar seus amigos... e ainda ganhar pontos com isso?
> Esse é o Vudú: o jogo em que você é um feiticeiro perverso... e a sua galera vira vítima.
> Na sua vez, você rola cinco dados de ingredientes. Não gostou? Guarda os que servem e rola de novo... mas cada nova rolagem custa um dado.
> Juntou os ingredientes da carta? Lança a maldição em alguém da mesa e marca pontos.
> E aí começa o caos! Na Kapoera, a vítima não pode encostar os pés no chão... Na Tutakobraço, tem que ficar com os braços esticados... e tem maldição muito pior.
> Esqueceu da maldição? Quem lançou ganha ainda mais pontos.
> Quem chegar primeiro nos onze pontos vence. De duas a oito pessoas, em uns trinta minutos.
> Quer amaldiçoar sua galera no fim de semana? Aluga o Vudú na Sua Vez: link na bio! E comenta aqui: qual maldição você jogaria no seu melhor amigo?

---

## Como gravar a narração

### Opção A — CapCut no celular (mais fácil, já sai sincronizado)
1. Abra o CapCut → **Novo projeto** → escolha `vudu_limpo.mp4`.
2. Toque em **Áudio → Narração** (ícone de microfone).
3. Deixe o cursor no início, segure o botão e fale acompanhando o vídeo.
   Use a página de teleprompter (link na conversa) em outra tela, ou a tabela acima.
4. Errou um trecho? Apague só aquele pedaço e grave de novo a partir dali.
5. Abaixe a música: toque no áudio original do vídeo → **Volume ~40%**.
6. (Opcional) **Texto → Legendas automáticas** para legendar com a sua voz.
7. Exporte em 1080p, 30 fps.

### Opção B — gravar o áudio separado e eu faço a mixagem
1. Grave no **Gravador de voz** do celular (ou WhatsApp, mandando para você mesmo),
   lendo o roteiro com o vídeo `vudu_limpo.mp4` tocando sem som em outra tela.
2. Comece a falar logo depois de dar play (o texto começa em 0:00,2).
3. Me mande o arquivo (.m4a, .mp3, .wav…). Eu rodo:
   `python3 reels.py mix --voz narracao.m4a`
   que baixa a música automaticamente quando você fala (ducking),
   nivela o volume da voz e gera `out/vudu_final.mp4`.

### Dicas de som
- Grave num cômodo com cortinas, sofá ou roupas (evite banheiro e cozinha).
- Celular a um palmo da boca, um pouco de lado para os "p" não estourarem.
- Faça 2 ou 3 tomadas completas: a segunda costuma ser a melhor.
- Se o trecho ficar comprido demais, corte palavras em vez de acelerar.

---

## Publicação (sugestão)

**Legenda do post:**
> Você teria coragem de amaldiçoar seus amigos? 😈🎲
> Vudú é o jogo em que cada rodada vira uma maldição hilária: ficar sem pôr o pé no chão, braços esticados, falar esquisito… e quem esquece perde feio.
> 👉 Alugue na Sua Vez, link na bio!
> 💬 Comenta: qual maldição você jogaria no seu melhor amigo?

**Hashtags:** #jogosdetabuleiro #boardgames #vudu #jogodetabuleiro #boardgamebrasil
#aluguedejogos #jogoscomamigos #noitedejogos #stopmotion #suavez

**Dica para monetizar/alcance:** vídeos acima de 1 minuto entram no programa de
recompensas do TikTok (Creator Rewards). A pergunta no final serve para puxar
comentários, que é o que mais impulsiona o alcance. Responda os primeiros
comentários com vídeo ou fixe o melhor.

---

## Créditos e observações
- Fotos e artes: jogo **Vudú (2ª edição)**, Red Glove / **MeepleBR**, de páginas
  de lojas online (arte oficial de divulgação). Uso para divulgar a locação do
  próprio jogo é prática comum, mas se quiser ficar 100% tranquilo, fotografe a
  sua cópia e troque os arquivos em `assets/pieces/` (mesmos nomes).
- O logo "SUA VEZ" é **provisório**. Salve o logo oficial (PNG com fundo
  transparente) como `assets/logo_suavez.png` e rode `python3 reels.py`
  de novo: marca d'água e tela final são atualizadas sozinhas.
- Conferir na caixa: 2 a 8 jogadores, 8+, ~30 min, vitória com 11 pontos
  (dados das lojas e do tabuleiro, que vai até 11).
