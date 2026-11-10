# Reels da Sua Vez – memória do projeto

Este repositório reúne os vídeos verticais (Reels/TikTok) dos jogos de tabuleiro da **Sua Vez**. Leia
tudo antes de começar um vídeo novo: aqui está o que funcionou, o que não funcionou e do que o dono gostou.

## Como continuar numa conversa nova (LEIA PRIMEIRO)

- Toda a memória do projeto está **neste arquivo** e no código da branch `claude/voodoo-stop-motion-video-rni4kj`
  (repositório erik-magalhaes/GitJoy). Numa sessão nova, use o mesmo repositório e a mesma branch: o Claude lê este
  arquivo sozinho. Brutos de vídeo e `out/` NÃO vão pro git; os brutos gravados estão no Drive dele
  (https://drive.google.com/drive/folders/1yGgKAxAUrJAipiu4p2687F4TaA8I6yCK, baixar com `python3 -m gdown`).
- **Pasta do Drive com os vídeos prontos para postar:** https://drive.google.com/drive/folders/1eAEc1ecYI5fPMZnaiccu8DJdXI-cXCAG
  (listar sem baixar: `gdown.download_folder(url, skip_download=True)`). Em 12/out faltavam lá: efeito "jogos modernos",
  bye bye curto, tarô, custo e Halloween pôster (mandei de novo pelo chat). Lá também há vídeos que ELES gravaram
  (Dungeon Fighter, O Vale dos Monstros II, Happy Salmon, Hitster, MicroMacro, Telestrations, Trio, Throw Throw Burrito,
  Scooby-Doo, Drácula vs Van Helsing, "pessoa que demora na vez"): contam como jogos já postados.
- **Google Drive conectado (14/out):** o Drive é um Drive compartilhado (raiz `0ACBVgpjsn6mwUk9PVA`, dono
  suavezjogosabc@gmail.com). Pasta **Videos** = `1eAEc1ecYI5fPMZnaiccu8DJdXI-cXCAG`; pasta **Carrosséis** =
  `15Vn5eW10vEVyU6cBrdUkbGus6OSeMqjD` (subpastas 01…10, uma por carrossel). O conector CRIA pastas, move e renomeia, mas
  só sobe arquivo com o conteúdo dentro da mensagem: imagem/vídeo de MB não dá. Então: eu organizo as pastas e mando os
  arquivos pelo chat (zip por carrossel), e ele salva no Drive. Em 14/out mandei os 10 carrosséis e os vídeos que faltavam
  na Videos (efeito, bye bye curto, tarô, custo, Halloween pôster, quiz com trilha, assinaturas, como alugar). Na Videos há
  duplicados (hobby, marvel e hotstreak 2x).
- **Estado em 10/out/2026:**
  - Entregues e aprovados: vídeo do Dia das Crianças v2 (`gravados-reels/criancas2.py`), cartão do evento 9x9
    (`promo/cartao_evento.py`), carrossel do feed "jogos modernos" (`hobby-reels/carrossel.py`, 8 telas 1080x1350; versão QUADRADA 1080x1080 que ele pediu para o feed em `carrossel_quadrado.py`, mesmas telas reposicionadas;
    na tela 4 o Go Cuckoo foi trocado pelo Gravity porque ele achou a foto "amassada").
  - **Esperando narração dele:** Final Girl e 7 tipos de jogador
    (links nas seções abaixo).
  - **Trend "5, 4, 3, 2, 1"** (`gravados-reels/lista54321.py`, gravado por ele, brutos no Drive 20261010_102656/102715):
    editado e mandado (ver seção "5, 4, 3, 2, 1" nas pendências).
  - **Esperando gravação dele:** vídeo de Halloween (roteiro já mandado).
  - Microfone dele (Kaidi, lapela sem fio): redução de ruído que NÃO desliga, som "robótico"; recomendei gravar com o
    microfone do celular a 30–40 cm em cômodo silencioso.

## A loja

- **PRIMEIRO ALUGUEL (5/nov/2026):** o cliente achou a Sua Vez pelo **ChatGPT**, que indicou a loja quando ele procurou a
  locação de um jogo específico em São Paulo. A partir daqui já existe cliente de verdade (antes: "nenhum aluguel ainda").
  Depoimento/foto só com autorização do cliente; nunca inventar números de aluguel.
  O cliente buscou o **Hitster Lado B**; no teste do Erik o ChatGPT mostrou a Sua Vez em 1º e uma loja mais barata em 2º,
  e o cliente escolheu a Sua Vez mesmo assim. Ele vai pedir avaliação e autorização para depoimento. **NÃO fazer post "nosso
  primeiro aluguel"** (eles já deram a entender em público que alugaram antes).

- **Donos: Erik e Jéssica.** A Jéssica também pede peças (13/out/2026). Endereço: **Av. da Saudade, 96 – Mauá**.
  Pagamento Pix ou cartão. Plataforma do site: Acervo de Jogos. **Categorias e preços avulsos:** Pocket R$ 15 / 5 dias,
  Família R$ 30 / 5 dias, Estratégico R$ 45 / 5 dias, **Deluxe R$ 60 / 7 dias** (só Final Girl, Flamecraft, Wonderland's
  War e Zombicide Rue Morgue). Acervo de **163 jogos**, a maioria Pocket e Família.
- **ASSINATURAS (lançadas em out/2026, já no site; só assinatura, sem "pacotes"):** **Silver R$ 49/mês** (1 jogo por
  vez, Pocket e Família) · **Gold R$ 89/mês** (2 por vez, + Estratégico) · **Platinum R$ 139/mês** (3 por vez, acervo
  inteiro, no máx. 1 Deluxe por vez). Devolve um e pega outro, **trocas sem limite no mês**; a taxa de entrega é cobrada
  a cada troca. Chamada: "assine pelo link na bio". O "Pacote Silves" (R$ 60 / 2 aluguéis) do site é para rever/desativar.
- **Identidade visual que a Jéssica passou** (usar nas artes dela, `assinatura-reels/estilo.py`): Lilita One (títulos) +
  Figtree (texto) em `assinatura-reels/assets/fonts/`; marrom #3F2412 (texto, contornos, sombra sólida), azul-petróleo
  #1C7C96 (Família), laranja #F48825 (Pocket), fundo azul-claro #E3F3F6, amarelo #FFC71F, branco #FAFAFA; contornos
  grossos marrons, sombra sólida deslocada, elementos levemente girados, selos em pílula, cara de tabuleiro; logo numa
  caixa branca com contorno. Legendas não repetem o texto da arte.

- **Sua Vez – Locação de Jogos de Tabuleiro**, Mauá e ABC (SP). Site: https://suavez.acervodejogos.com.br/
  (o logo veio de lá: `*/assets/logo_suavez.png`). Instagram: **@suavez_bg**.
- Aluguel de **5 dias**, com reserva online e **retirada em Mauá ou entrega em casa** (existe uma pequena taxa de entrega,
  mas ele pediu para **não citar a taxa** nas artes; o frete é combinado no checkout). Promoção de **prazo progressivo** (vale para todos os jogos do carrinho, pelo mesmo preço):
  **3 jogos = 7 dias, 5 jogos = 10 dias, 7 jogos = 15 dias** (arte em `promo/promo_progressivo.py`).
  CTA padrão: "aluga na Sua Vez, o link tá na bio". Não escreva só "retire em Mauá": cite também a entrega.
- O dono fala português do Brasil, usa **o celular** para quase tudo e grava a narração ele mesmo.

## REGRA (6/nov/2026): toda peça em 3 formatos

- **Tudo que eu fizer, pensar em Reels, carrossel e Stories** (pedido dele). Vídeo: versão Reels (CTA "comenta",
  WhatsApp/link na bio, sem buraco) e versão Stories (espaço LIVRE no MEIO, y≈1350–1580, para o adesivo de link, com
  "garanta sua mesa aqui:" + seta). Carrossel 1080x1350 + as mesmas telas como Stories 1080x1920 (tela no meio, y 285–1635;
  último Story com o espaço do link). Ver `becas-reels/no_becas.py` (`--reels`/`--stories`, `salva()`, `story_de()`).

## O que todo vídeo precisa ter

- Formato 1080x1920, com **duração entre 1:00 e 1:10**. Passar de 1 minuto é obrigatório porque é o que monetiza.
- **Gancho** forte nos primeiros 2 segundos: uma pergunta ou provocação, com o texto já na tela.
- Marca d'água com o **logo da Sua Vez** no canto superior direito o vídeo inteiro (menos na tela final).
- **Tela final** com o logo, a caixa do jogo, "ALUGUE O ...", jogadores/tempo, "5 dias de jogo",
  "RESERVE ONLINE · RETIRE EM MAUÁ E ABC" e "LINK NA BIO · @SUAVEZ_BG".
- **Chamada para comentar** antes do CTA, com uma pergunta divertida sobre o jogo ("Comenta aqui!").
- Explicar as regras **certas**, conferindo no manual. Para isso servem o kit de imprensa e o Board Game Arena (veja Fontes).
- Entregar duas versões: **com legenda** e **sem legenda**. Loudness final de **≈ -14 LUFS**.

## Fluxo de trabalho que funciona

1. Escolher um **conceito visual diferente dos vídeos anteriores** (veja "Preferências"). Para decisões visuais,
   mande **imagens de comparação** com 2 ou 3 opções lado a lado. Funcionou muito bem para escolher o visual do Arquitetos.
2. Escrever o **roteiro em 9 falas curtas**, uma por cena, num total de ~55 s de fala. Mandar o roteiro no chat.
3. Fazer a **prévia** sem voz (trilha + legendas do roteiro) e mandar a versão 720p (`-b:v 2800k`) pelo chat.
4. Mandar o **link da página de gravação** sem o dono precisar pedir. Ele sempre pede ("lembra de me passar a narração").
5. O dono manda **9 arquivos .webm**, normalmente na ordem das falas. Ele **muda palavras** quando grava:
   o vídeo e as legendas seguem o que ele **falou**, não o roteiro.
6. Tratar, transcrever, encaixar (`narracao.py` → `narracao/timeline.json`), renderizar as duas versões e
   ajustar o volume. Depois conferir alguns quadros antes de mandar.

### Página de gravação (o que funcionou)

- Modelo: `voodoo-reels/gravador/Gravar_narracao_Vudu.html`, baseado no HTML que o próprio dono mandou. Cada fala tem
  o botão Gravar/Parar, o player e um medidor. No fim, "Baixar / enviar todas" usa `navigator.share` no celular. Os arquivos
  se chamam `<jogo>_narracao_NN`.
- Hospedar pelo **raw.githack.com com o hash do commit**, para ter HTTPS e o celular liberar o microfone. Exemplo:
  `https://raw.githack.com/erik-magalhaes/GitJoy/<commit>/architects-reels/gravador/Gravar_narracao_Arquitetos.html`.
  Antes de mandar o link, confira que ele responde 200.
- **Não funcionou:** gravar dentro de um Artifact (o microfone fica bloqueado), abrir o HTML local no navegador
  (não pede permissão do microfone) e gravar por cima do vídeo (ele quer gravar separado e que eu encaixe).

### Tratamento da voz (receita que deu certo)

- ffmpeg: `highpass=f=80, afftdn=nr=12:nf=-45:tn=1, equalizer 250 Hz -2.5 dB, 3200 Hz +3 dB, 9000 Hz (shelf) +1.5 dB,
  deesser=i=0.35, acompressor=threshold=-20dB:ratio=3:attack=6:release=140:makeup=3dB, loudnorm=I=-16:TP=-1.5:LRA=6`.
- Corte de silêncio por energia em numpy e reamostragem para **44,1 kHz** (a trilha usa SR=44100). Veja
  `mlem-reels/tratar_narracao.py`, que gera `frase_NN.wav` e `palavras.json` com faster-whisper `small`, int8, pt e tempos por palavra.
- `narracao.py` monta a linha do tempo: cada cena estica ou encolhe para caber a fala (LEAD 0,3 / GAP 0,45 / TAIL 0,6,
  CTA_HOLD 3,6 s e cena com no mínimo 70% da duração original). As legendas seguem os tempos reais das palavras.
- A trilha abaixa sozinha (ducking) quando há voz. Depois do render, suba ~**+1,6 dB** com `alimiter` para chegar a ≈ -14 LUFS.
- **Revise a transcrição:** o Whisper erra nomes e piadas. Já confundiu "Ô, Luisa Mell!" com "O Luís Améu",
  "MLEM" com "Milam" e "o capitão rola os dados" com "Capitão Rallos Dados". Corrija o `TEXTO` no `narracao.py`.

## Os vídeos feitos até agora

| Pasta | Jogo | Visual | Resultado |
|---|---|---|---|
| `voodoo-reels/` | Vudú | **Stop motion** de fotos reais recortadas, 12 poses/s com tremidinho, mesa escura e textos em adesivo branco (LuckiestGuy) | Aprovado, 1:06 |
| `sintonia-reels/` | Sintonia | **Motion graphics vetorial**, com os balões "CLARO!" na hora da discussão | Aprovado, 1:03 |
| `mlem-reels/` (`gibi.py`) | MLEM: Agência Espacial | **Gibi**: página de quadrinhos em que a câmera dá zoom num quadro por vez e o foguete atravessa os quadros com fumaça | Aprovado, 1:06 |
| `architects-reels/` (`stopmo.py`) | 7 Wonders Arquitetos | **Stop motion** com as peças oficiais sobre **papel quadriculado** (tema "prancheta"), com textos em fita crepe escritos à mão | **Narrado e entregue** (69,9 s, com e sem legenda) |
| `hobby-reels/` (`ludoteca.py`) | Institucional: o que são jogos modernos + preço loja × aluguel + prazo progressivo | **Estante da ludoteca** (opção 1): caixas do acervo em prateleiras de madeira, caixas saindo em stop motion, etiquetas kraft e de preço | **Narrado e entregue** (1:08, com e sem legenda) |
| `quiz-reels/` (`relampago.py`) | Quiz "Que jogo é esse?" (5 caixas do acervo) | **Zoom relâmpago** (opção 3 de `conceitos.py`): detalhe da arte em TELA CHEIA, anel de contagem 3 s, abre rápido para a caixa inteira sobre a própria arte desfocada; 25 s, sem narração. A versão com lupa (`zoom.py`, 1:05) foi REJEITADA: "feio, dinâmica ruim, longo" | Mandado (para_musica + com_trilha) |
| `byebye-reels/` (`curto.py`) | Trend "bye, bye, Miss American Pie": Banco Imobiliário → jogos modernos | **Vídeo curto (12 s, sem som)**: Banco Imobiliário aberto na mesa de madeira, com cor lavada, passando; no "tchan" (3,0 s) flash e vira para o Hot Streak (foto oficial) e o Ticket to Ride: Lendas do Oeste, e fecha com a Sua Vez. A versão longa com polaroides (`byebye.py`) foi REJEITADA ("ficou horrível") | Mandado |
| `tipos-reels/` (`tipos.py`) | Os 7 tipos de jogador que todo grupo tem | **Cartas colecionáveis** com raridade, status, habilidade e jogo favorito; pacotinho rasgando, carta virando, brilho holográfico | Prévia mandada; esperando a narração |
| `marvel-reels/` (`portais.py`) | Os 9 Marvel United do acervo + Multiverse chegando | **Portais do multiverso** (opção 1) com pegada de **filme de herói**: arte da capa dentro de portais de faíscas, caixas 3D e miniaturas recortadas saindo dos portais, holofote, brilho de lente, faixas de cinema e acabamento limpo em HD (sem granulado), trilha de trailer | **Narrado e entregue** (1:08, com e sem legenda; 1080p em 2 passadas a 3250k para caber em 30 MB) |

Comandos comuns: `python3 <script>.py --frame T [T2 ...]` (quadros de teste em `out/frames.jpg`), `--only preview`
e sem argumentos (gera com e sem legenda). Os vídeos ficam em `out/`, que **não vai pro git**.

## Preferências do dono (gostou / não gostou)

- **Cada vídeo precisa ter uma cara própria.** No 7 Wonders ele gostou do stop motion, mas pediu para "afastar do Vudú".
  A solução foi manter a animação e trocar a mesa, a luz e o estilo dos textos.
- Gosta de stop motion **limpo**: peças retas e bem recortadas, sombra suave e o tremidinho da mão. Se o recorte ficar ruim, o vídeo todo fica ruim.
- Gosta de **detalhe e ação na tela**: dados rolando de verdade, peça saindo de um quadro para outro, fumaça, som em
  cada ação e a peça virando como no jogo de verdade (a maravilha passando de "em obras" para "construída").
- O roteiro precisa ser **claro**, na ordem de uma jogada real, e o CTA precisa ser forte. Ele já reclamou de roteiro confuso e de CTA fraco.
- **Nunca deixar texto cortado:** nada fora da tela, atrás da legenda (y > ~1590) ou atrás do logo.
  No gibi, o zoom cortava palavras e foi resolvido com `auto_cam` (enquadra o quadro inteiro mais os balões, numa área segura).
- A ação na tela tem que bater com a regra. No MLEM, o gato que "desce cedo" precisa pular **no começo** da trilha,
  e não no fim.
- **Não gostou de:**
  - massinha/claymation (no Vudú ele queria as peças reais, não massinha);
  - arte vetorial genérica para o MLEM;
  - recorte de fotos de celular em perspectiva (cartas "tortas/diagonais");
  - gatos e dados recortados à mão de foto;
  - stop motion tremido demais;
  - a planta azul (blueprint) com fotos tortas presas na folha.

## Fontes de imagem (do melhor para o pior)

1. **Kit de imprensa da editora.** No 7 Wonders foi o que salvou: https://www.rprod.com/en/press/<jogo>. O zip "BR"
   traz cartas retas em alta resolução, os tabuleiros de peças com transparência (os dois lados), caixa 3D, logo e o
   manual em PDF. `architects-reels/pecas_oficiais.py` mostra como extrair tudo, inclusive renderizar fichas vetoriais do
   PDF com PyMuPDF (`pip install pymupdf`). Imagens rasterizadas pequenas do PDF ficam pixeladas; prefira as vetoriais.
2. Fotos de produto de lojas brasileiras. Bravo Jogos (CDN simplo7, imagens 2000 px) e Two Head Games funcionaram com `curl -A Mozilla/5.0`.
   Fotos de peças em **fundo preto** recortam bem por limiar; já as fotos de celular em cima da mesa recortam mal.
3. BoardGameGeek e Ludopedia respondem 403 e a loja da Galápagos responde 401 pelo proxy. Não dá para depender deles.
4. Para conferir regras: a página de ajuda do jogo no Board Game Arena (en.doc.boardgamearena.com) e o manual do kit.

## Dicas técnicas (pegadinhas já resolvidas)

- Render: PIL/numpy gera os quadros e manda para o ffmpeg (`imageio_ffmpeg`), com `Pool(4)`. Um vídeo de 66 s a 30 fps leva ~10 min
  (o stop motion a 12 fps é bem mais rápido). Rode renders longos **em segundo plano** (`run_in_background`), sem `&`
  dentro do comando, porque o processo morre ou o log se perde.
- Pillow 12: bbox de texto vem em float, então arredonde com floor/ceil. `Image.resize(box=...)` não aceita caixa fora da
  imagem (deu erro no tremor da cena de guerra), então limite a caixa à imagem.
- Cuidado com `pkill`, que já matou o próprio shell. O `rm` combinado com `cd` é bloqueado, então use caminhos absolutos.
- Recortes: casco convexo resolve peças convexas (fichas e marcadores). Para fundo branco, use flood fill a partir das bordas;
  para fundo preto, use limiar com o maior componente. Peças de tabuleiro com transparência oficial são sempre melhores.
- Peças de dois lados (maravilha do 7 Wonders): o lado "construído" é o **verso**, então fica espelhado. A coluna da esquerda
  em obras vira a da direita construída (veja `VERSO` em `stopmo.py`).
- Estilos de texto prontos: adesivo de papel (`stopmo.sticker`, visual do Vudú), fita crepe, placa de pedra e tira
  de papel colorido (`architects-reels/temas.py`), além dos balões, caixas de narração e onomatopeias de gibi (`mlem-reels/gibi.py`).
- Trilha sintetizada em numpy (`voodoo-reels/audio.py`, `sintonia-reels/trilha.py`, `mlem-reels/som.py`,
  `architects-reels/trilha_arq.py`), com efeitos sincronizados por `cues` e `warp()` que acompanha o tempo da narração.

## Pendências

- **7 Wonders Arquitetos:** **narração recebida (10/out/2026)**: de novo os 9 .webm vieram SEM nome e na ordem INVERTIDA, e
  as falas 6 (vermelhas) e 7 (verdes) vieram gravadas trocadas; encaixei pela cena (cena 6 = guerra). A fala dele somou 81 s
  de vídeo: pausas internas ≤0,3 s (`encurta_pausas`), voz 1,10x (`atempo` antes da cadeia), LEAD/GAP/TAIL 0,2/0,4/0,35 e
  CTA_HOLD 2,4 → 69,9 s. A fala 9 virou "Um jogo que funciona pra casal e até 7 jogadores. Aluga o 7 Wonders Arquitetos...".
  Tela final ganhou "OU RECEBA EM CASA". Entregue a −15,5 LUFS, 2 passadas a 3000k (~28 MB). Antes era: esperando os 9 áudios. Gravador:
  `https://raw.githack.com/erik-magalhaes/GitJoy/6a9efbbc00e888124e30d4c5bd710ad1c6dd2bf6/architects-reels/gravador/Gravar_narracao_Arquitetos.html`.
  Ao receber: copie os áudios para `architects-reels/narracao/raw/`, trate (`tratar_narracao.py`), revise o `TEXTO` em
  `narracao.py`, rode `python3 narracao.py` e depois `python3 stopmo.py`, suba o volume e mande as duas versões.
  O kit de imprensa não está no repositório. Se precisar das peças de novo, baixe o zip BR e rode `pecas_oficiais.py <pasta>`.
- **Nekojima:** o dono não gostou e pediu para **apagar** o vídeo do projeto (out/2026). A pasta `nekojima-reels/` foi removida
  (fica no histórico do git). Só os sons base foram mantidos, em `comum/som_neko.py`, porque as trilhas do Hot Streak,
  do Marvel United e do hobby usam esses sons. Lição que fica: recorte só funciona com material oficial (peças com
  transparência) ou foto feita para isso (fundo liso e contrastante); antes de animar recortes, mande um quadro de teste.
- **Arte de promoção** (`promo/promo_progressivo.py` é a atual, com os degraus 3/5/7 jogos; a antiga é `promo/promo_3jogos.py`): "3 jogos = 7 dias para todos", em feed e story, com as cores e a fonte do site.
  Ele achou estranha a frase "em vez de 5, sem pagar nada a mais"; a que ficou foi "+2 dias de presente, pelo mesmo preço!".
  Os preços variam por jogo (exemplos do carrinho: Bad Company R$ 45, Art Society R$ 30 por 5 dias).
  **Flyer impresso para evento** (`promo/flyer_evento.py`, out/2026): A5 a 300 dpi (PNG + PDF) e A4 com 2 por folha; logo,
  "ALUGUE JOGOS DE TABULEIRO / e jogue em casa por 5 dias", 160 jogos a partir de R$ 15, 3 passos (reserve, retire em
  Mauá ou receba em casa, jogue 5 dias), escada 3/5/7 → 7/10/15 dias, cupom do evento **JOGAMAUA5 = 5% de desconto na
  locação** (ele disse "Joga Mauá 5") e QR code do site (conferido com o leitor do OpenCV).
  Ele achou o flyer "detalhado demais" e mandou de referência um cartãozinho de cookie (quadrado, fundo claro, uma cor,
  enfeites cortados nos cantos). Ficou `promo/cartao_evento.py`: **9 x 9 cm**, logo, "Bora jogar? / Alugue jogos de
  tabuleiro e jogue em casa por 5 dias!", QR + cupom JOGAMAUA5 5% OFF, @suavez_bg; A4 com 6 cartões e marcas de corte
  para imprimir em papel comum. Para impressos curtos: pouco texto, QR grande.
- **Hot Streak (`hotstreak-reels/`):** é da CMYK, com 4 mascotes (Hurley, o cachorro-quente; Gobbler, o urso; Dangle,
  o peixe-pescador; Mum, a rainha). São 3 corridas, 2 bilhetes por corrida em draft cobra, aposta segura ou arriscada,
  apostas paralelas SIM/NÃO e uma carta secreta de cada jogador no baralho. Mascote cai, dá meia-volta, desvia de raia e bate;
  é desclassificado se cair já caído ou sair da pista; vence quem tiver mais dinheiro. **Nomes da edição brasileira (Galápagos), confirmados pelo dono:** **Jiba** (a salsicha), **Gluglu** (o urso),
  **Brinco** (o peixe) e **Mona** (a rainha). Nunca use os nomes em inglês. Os bilhetes foram adaptados por
  `recortes_hs.bilhetes_br()` ("Gluglu" e "SIM"). Final pedido por ele: "PARA TUDO! Em quem você aposta? Comenta aqui!",
  seguido de uma corridinha (cena 9, sem fala) em que o Gluglu capota e o **Brinco ganha** na foto de chegada.
  **Material:** o manual em PDF
  (`assets/manual.pdf`) é todo vetorial. `vetor_hs.py` redesenha só os traços escolhidos e gera recortes PERFEITOS em qualquer
  resolução: os mascotes do pódio (`p_*.png`), a torcida sem o QR da editora (`v_torcida_limpa.png`) e os bilhetes. Os bonecos
  de vinil da foto oficial (Shopify da CMYK, 6000 px) recortam bem por chave de verde (`recortes_hs.py`). **Conceito escolhido:
  2, Arquibancada** (arte do jogo: torcida, pista verde, confete, placas). Teste e roteiro aprovados ("Sim").
  **Vídeo completo em `hs.py`** (66 s, 9 cenas): gancho com torcida e Hurley; largada com nomes; guichê de bilhetes
  (creme com borda vermelha e lâmpadas); bilhete virando de "Safe" para "Risky"; telão com a ilustração das cartas
  secretas e a carta entrando no baralho; corrida com casas, cartas virando embaixo (o Dealer) e legendas; DQ por queda
  dupla e por sair da pista; pilhas de dinheiro e tela VS para o "Comenta aqui!"; CTA com a caixa recortada
  (`recortes_hs.caixa()`, foto em fundo vermelho). As cartas de corrida do PDF são imagens de 151 px (pixeladas), então
  `hs.carta()` redesenha as cartas no estilo do jogo. Trilha própria: `som_hs.py` (galope, corneta, caixa registradora,
  buzina de DQ). Transição: bandeira quadriculada. A prévia foi mandada e estamos esperando os 9 áudios
  (`hs_narracao_NN`). **Narração recebida (out/2026):** a fala 7 diz "foi atropelado, desclassificado" (pelo manual,
  atropelado de pé só cai). Eu cortei o trecho e ele mandou voltar: **não mexa no que ele falou, mesmo que a regra não
  bata 100%** (no máximo avise). Voz acelerada 1,086x (atempo 1,06 × 1,025), corridinha a 62% e CTA_HOLD 2,3 → 69,5 s. **Narrado e entregue** (com e sem legenda).
  Gravador:
  `https://raw.githack.com/erik-magalhaes/GitJoy/24baf7085f0f95b8c9618b54b379541b9fecb2b5/hotstreak-reels/gravador/Gravar_narracao_HotStreak.html`.
  **POV "tô só correndo na rua... olho pra trás... tô DENTRO do Hot Streak" (`hotstreak-reels/pov_corrida.py`, 9/nov,
  ideia dele):** ele NÃO quer Gemini nem gravar ("é você criar, igual os outros") → tudo desenhado aqui: rua em
  perspectiva de verdade (`proj`, casas/muros/árvores/postes chapados no estilo do jogo, balanço do passo, horizonte da rua
  mais baixo `DY_RUA`), "TUM TUM!", chicote com borrão pra trás, os 4 mascotes OFICIAIS (p_*.png) correndo atrás na rua,
  bandeira quadriculada (`HS.bandeirada`) → pista do jogo em 1ª pessoa com a torcida oficial, confete, os mascotes
  ultrapassando com o nome BR (JIBA, GLUGLU, BRINCO, MONA) → "E VOCÊ, EM QUEM APOSTA? COMENTA AQUI!" → `HS.cena_cta`.
  24 s, sem narração, `pov_{com_som,para_musica}_final.mp4` (passos, respiração, galope depois da virada).
  `foto_gemini.py` (imagem da pista pro Gemini) ficou sem uso.
  **2ª rodada (9/nov): "o começo correndo como VIDA REAL; olha pra trás e vê os bonecos numa rua normal; olha pra frente e
  é a pista".** A rua desenhada saiu: `rua_real()` usa a gravação DELES no caminho do Beca’s (151125, 12–23 s = calçada
  da Matriz sem placa de carro → `out/rua_real/`, 30 q/s, leve hqdn3d/contraste) a 2x com balanço de corrida; olhando
  pra trás = o MESMO trecho de trás pra frente (sem espelhar: a placa da Alquifarma ficava ao contrário) com os mascotes
  pisando na calçada (sombra cinza, sprite descido 0,07h); olhar pra frente = chicote no sentido contrário direto na pista.
  **3ª rodada (9/nov): "não usa esse vídeo, usa um da internet sem direitos; não gostei de ficar DESCREVENDO; só
  correndo e depois dentro do jogo com 'é assim que você se sente jogando Hot Streak'"** → `hotstreak-reels/sente.py`
  (18,5 s): 3 planos de gente correndo do **Mixkit** (licença gratuita, sem atribuição; mixkit.co e assets.mixkit.co
  passam pelo proxy, Pexels/Pixabay dão 403; `https://assets.mixkit.co/videos/<id>/<id>-2160.mp4`; brutos em
  `hotstreak-reels/brutos/stock/`, fora do git): 40765 pés (P&B), 40748 moça vindo, 717 rapaz de costas; recorte 9:16 em
  `out/stock/` → chicote → pista em 1ª pessoa com os mascotes passando (sem nomes) + "É ASSIM QUE VOCÊ SE SENTE JOGANDO /
  HOT STREAK!" → `HS.cena_cta`. Sem gancho escrito na corrida (pedido dele). Busca de clipes: páginas
  `mixkit.co/free-stock-video/discover/<termo>/`, ids e títulos nos links `/free-stock-video/<titulo>-<id>/`.
  **4ª (9/nov): "precisa ser PRIMEIRA PESSOA, o olhar de quem corre"** → um plano só: Mixkit **40656** (POV andando num
  caminho de parque, já 1080x1920; o 4K não baixa, só o `-1080.mp4`) a 2x (`setpts=0.5*PTS`) + balanço de corrida
  (zoom 1,16 pra não aparecer borda na inclinação). Outros POV de caminho no Mixkit: 28827 (passarela no outono, deitado).
  **5ª (9/nov, "esse vídeo tá perfeito"):** + OLHA PRA TRÁS: o mesmo vídeo ESPELHADO e de trás pra frente com os 4
  mascotes vindo correndo no caminho (`atras()`, horizonte `DY_PARQUE`), e ao olhar pra frente de novo (chicote no sentido
  contrário) já é a pista; frase: "É ASSIM QUE VOCÊ SE SENTE QUANDO JOGA / HOT STREAK!". 20,5 s.
  **6ª ("tá legal"; a transição tem que PARECER a pessoa olhando pra trás e pra frente; o olhar pra trás longo):**
  `chicote()` virou um GIRO DE CABEÇA (faixa a|b deslizando com borrão forte, zoom 1+0,26·sen que esconde os cantos da
  inclinação de 8°, cabeça abaixando 50 px no meio, 0,55 s), sem flash branco ao chegar na pista; olhar pra trás 1,8 s. 18,8 s.
- **Reels do hobby (`hobby-reels/`):** ele pediu um vídeo explicando os jogos modernos para quem não conhece o hobby,
  com a comparação de preço (loja × aluguel) e a promoção progressiva. Escolheu o visual 1 (estante) e pediu que **eu mesmo
  fizesse a narração, "sem cara de IA"**. Voz: `pt-BR-AntonioNeural` (edge-tts), gerada por `gerar_voz.py`. O edge-tts
  funciona pelo proxy com o CA `/root/.ccr/ca-bundle.crt` (veja `tts.py`). Para soar natural: velocidade +12–16% e tom
  variando por fala, pausas internas cortadas para ≤0,3 s (`tratar_narracao.encurta_pausas`) e escrita fonética
  ("Uíngspan"). Amostras das vozes (Antonio, Thalita, Francisca) foram mandadas e ele ficou com a primeira.
  **Resultado: ele achou as vozes "muito robóticas" e decidiu narrar ele mesmo.** Não ofereça voz sintetizada de novo
  sem ele pedir. A versão sintetizada ficou guardada em `narracao_tts/`. O fluxo voltou ao normal: prévia sem voz +
  gravador `gravador/Gravar_narracao_Hobby.html` (arquivos `hobby_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/bfa6b27128ef7ce4e1690c26d256c9957c564344/hobby-reels/gravador/Gravar_narracao_Hobby.html`.
  **Narração recebida (out/2026):** os 9 .webm vieram SEM nome e na ordem INVERTIDA (o 1º arquivo era a fala 9): sempre
  transcreva antes para saber de qual vídeo e de qual fala é cada um. A fala dele somou 61 s, então apertei
  LEAD/GAP/TAIL para 0,2/0,4/0,35 e CTA_HOLD para 3,0 (vídeo de 1:08). O render já sai a ≈ -14 LUFS.
  **Correções pedidas:** (1) recortes com sobra laranja (Flamecraft): resolvido "descascando" de fora para dentro as regiões
  com cor de fundo/sombra ligadas à borda antes do casco convexo; (2) **não dizer "jogo bom é caro"** (existe jogo bom e barato).
  A fala ficou "os jogos modernos costumam ser caros... por isso alugar faz tanto sentido".
  (3) Marvel United saía torto porque a foto do site é só a arte da capa, sem a caixa 3D (vale para todos os Marvel United):
  trocado por The Goonies (cooperativo). (4) A parede do final repetia caixas: agora usa `assets/acervo/` (105 caixas
  diferentes e bem recortadas, de 161; a lista está em `assets/acervo_bons.txt`, escolhida no olho, porque a medida
  automática `sobra_laranja` confunde arte laranja com sobra). Recorte em lote: `python3 recortes_caixas.py acervo`.
  **Fotos das caixas:** o site da Sua Vez (`/boardgames?page=N`) tem renders 3D de 1024 px em fundo laranja liso;
  `recortes_caixas.py` recorta com GrabCut + modelo do degradê + remoção da sombra + casco convexo. Caixas laranja
  (Cores com Dicas, Patchwork, Sushi Go, Splendor, Dinosaur Island) saem com sobra e foram descartadas.
  **Preços (out/2026):** aluguel de R$ 15, 30, 45 ou 60 por 5 dias, com 160 jogos no acervo; Wingspan a partir de R$ 377 nas lojas
  (Compara Jogos) e R$ 45 no aluguel; Clank! Catacombs a partir de R$ 422 (R$ 45); Hot Streak a partir de R$ 279 (R$ 30).
- **Marvel United (`marvel-reels/`):** ele pediu "bem recortado, numa pegada filme de heróis" e escolheu os **portais** (opção 1).
  No acervo há **3 jogos base** (Marvel United, X-Men, Spider-Geddon) e **6 expansões** (Civil War, Blue Team, Gold Team,
  Deadpool, Rise of the Black Panther, Enter the Spider-Verse), todos a R$ 30. Pedido dele: destacar que **1 base + 2 expansões
  = 3 caixas = 7 dias** (prazo progressivo). O "vilão controlado por jogador" já existe no X-Men (Modo Supervilão), então
  não é novidade do Multiverse. O Multiverse é da Galápagos (jan/2025, ~R$ 330, 1 a 5 jogadores) e "vem aí" para o acervo.
  **Material:** as fotos do site da Sua Vez são só a arte da capa (sem caixa 3D). As fotos 3D e das miniaturas em fundo branco
  vieram da Bravo Jogos (2000 px). As capas das outras expansões vieram do Compara Jogos (`og:image`). `recortes_marvel.py` faz:
  caixas 3D por flood fill + casco convexo; caixas montadas a partir da capa (frente, lateral e tampa); e miniaturas
  separadas uma a uma, tirando os vãos brancos fechados. Na mão de cartas, NÃO tire os brancos internos.
  **2ª rodada (pedido dele):** os recortes de caixa estavam ruins, então troquei pelas **fotos 3D oficiais da Spin Master/CMON**.
  As lojas Shopify publicam essas fotos: dá para buscar com `/search?q=...` e ler `/products/<handle>.json`. Usei The Game Steward,
  Gameology e Riftgate (nomes do tipo `smy..._web_box_3d_l.jpg`). O Gold Team só tem a capa, então a capa foi aplicada em
  perspectiva na foto 3D oficial da Blue Team, que tem o mesmo formato (`caixa_no_molde`). O Civil War oficial tem a lateral branca
  e o recorte falha; ficou a foto da Bravo. Cada portal mostra a caixa **de onde saem** as miniaturas (não pôr capa do X-Men com
  as miniaturas do jogo base). O gancho virou um **elenco inteiro** saindo do portal (miniaturas de várias caixas, em duas fileiras).
  **3ª rodada:** ele quis um **paredão com todas as miniaturas** ("mostrando tamanho, diferença"). Ficou em `paredao()`: 5 degraus de
  vitrine com ~49 miniaturas de 8 caixas, todas na mesma escala graças à `REF`, que dá a altura de uma miniatura comum em cada
  foto (cada foto de loja tem um zoom diferente). Fotos de miniaturas em fundo branco da Zatu (Shopify, 1024 px): Deadpool,
  Blue Team, Gold Team e Multiverse. A Zatu também tinha a caixa 3D oficial do Gold Team. As miniaturas do Multiverse saem do
  portal gigante na cena "vem aí".
  **4ª rodada:** as fichas de seta e de soco (recortadas em ângulo de uma foto da Bravo) ficaram tortas e ruins. Agora uso os
  **ícones oficiais de ação** do manual da CMON (`https://cmon-files.s3.amazonaws.com/pdf/assets_item/resource/202/Marvel_United_Rulebook.pdf`,
  pág. 8): `icones_oficiais.py` troca a textura de papel do fundo por uma imagem transparente e renderiza a página com alfa a 1000 dpi
  (os ícones têm degradê, então o redesenho traço a traço do Hot Streak não serve). Resultado: `icone_{mover,atacar,heroica,coringa}.png`.
  **Dica geral:** para símbolos de jogo, o manual oficial em PDF é a melhor fonte.
  Gravador: `https://raw.githack.com/erik-magalhaes/GitJoy/3d0afc99e9c3cdc65a416b73ad54dfbbcbe784b3/marvel-reels/gravador/Gravar_narracao_Marvel.html`.
- **Qualidade de imagem (lição do Marvel United):** ele NÃO gosta de granulado de filme nem de nada que pareça ruído ou
  pixel ("quero HDzão de cinema"). Use acabamento limpo: vinheta suave, movimento liso a 30 fps no estilo trailer (sem tremidinho),
  luz de recorte fina e nítida (sem halo borrado), recortes passados por `fastNlMeansDenoisingColored` + `UnsharpMask`
  (tira os bloquinhos de JPEG das fotos de loja), x264 com `-crf 16 -tune film` e prévia 720p a ~6000k em fundos escuros
  com degradê (a 2800k aparece blocagem). O chat aceita arquivos de no máximo 30 MB: para ~66 s, use x264 em duas passadas
  a ~3300k (`-preset slow -tune film -pass 1/2`), que fica com ~28 MB.
- **Engajamento (out/2026):** ele reclamou de visualizações e engajamento baixos. Explicar regras não gera marcação nem
  comentário; os formatos novos são entretenimento: **marcar o amigo** (tipos de jogador), **quiz** (palpite nos comentários,
  assistir de novo) e **trend com música em alta**. Vídeo para música em alta: SEM narração, tudo escrito na tela, entregue
  em duas versões: `_para_musica` (só efeitos, ele põe o áudio da trend no Instagram) e `_com_trilha` (reserva).
  No quiz ele pediu jogos **mais difíceis** e escolheu a lista: Ticket to Ride, King of Tokyo, Codinomes (no acervo é o
  **Código Secreto Imagens**), Deep Regrets e Segue o Fluxo. O zoom nunca pode mostrar o título nem a borda da caixa.
  Trend: vídeo de trend é CURTO (ele disse que não precisa de 1 minuto) e a ação tem que bater com a música; a ideia boa
  foi dele: jogo antigo → "tchan" → jogo moderno. Eu não tenho acesso à música (direitos autorais): ele põe o áudio no
  Instagram. Se ele mandar o áudio da trend (gravação de tela), dá para achar o tempo exato do "tchan" e mudar `VIRADA`.
  **A trend é o "efeito Suíça"** (referência em `byebye-reels/referencia/`, fora do git): "antes" feio (calçada esburacada)
  até o silêncio da música, e no "tchan" (a música volta em 10,16 s; corte em 10,10 s) vira o "depois" bonito (Suíça), com
  o texto fixo 'O efeito "Suíça" 🇨🇭' (branco, contorno preto, y≈660). Cortes medidos: antes 0 / 4,67; depois 10,10 / 12,47 /
  14,40 / 16,43; fim 22,17. `byebye-reels/efeito.py --antigo ... --moderno ...` monta tudo com os clipes dele e o áudio da
  referência ('O efeito "jogos modernos" 🎲'), em versão com e sem música.
  **Feito (1ª versão):** ele gravou 5 clipes no celular (HEVC 1080p girado; em `referencia/clipes/`, fora do git):
  c1 Quest e c2 Imagem & Ação (antigos), c3 Santorini, c4 Luxor e c5 Hot Streak (modernos). Comando usado:
  `python3 efeito.py --planos c1.mp4:2.0 c2.mp4:0.5 c3.mp4:0.3 c4.mp4:1.6 c4.mp4:4.6 c5.mp4:2.0` (os caminhos estão em
  referencia/clipes). Cor (`grade()`, pedido dele "dar um tchanzão"): denoise + normalize + curva em S + correção do amarelo
  da lâmpada + nitidez nos dois; no depois, vibrance, bloom suave, vinheta leve e flash branco de 0,3 s no "tchan". Saída com e sem música, 22 s, ~26 MB.
  Fotos: Banco Imobiliário aberto do site da Estrela (`estrela.fbitsstatic.net/img/p/banco-imobiliario-150398/336914-1.jpg`),
  Ticket to Ride Lendas do Oeste da Gameology (Shopify), Hot Streak `hotstreak-reels/assets/fotos/HS4751.jpg`.
  Código comum dos três: `comum/motor.py` (animação, textos, legendas, render, prévia) e `comum/som.py` (trilhas
  gameshow/travessa/retro70 e efeitos). Emojis coloridos: Noto Color Emoji (`motor.emoji`). Vídeos de animação a 1080p
  ficam com < 30 MB, então dá para mandar o 1080p direto no chat.
  Caixas laranja do site (fundo laranja) recortam mal no automático: Código Secreto e Deep Regrets foram recortados à mão
  com um polígono de 6 pontos (caixa 3D) em `hobby-reels/assets/caixas/`.
  **7 tipos:** gravador `tipos-reels/gravador/Gravar_narracao_Tipos.html` (arquivos `tipos_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/5da0dc105532cf7d29b3ef270d4c72a131ff5c29/tipos-reels/gravador/Gravar_narracao_Tipos.html`.
  Ao receber: `narracao/raw/` → tmp_NN.wav (cadeia de voz) → `tratar_narracao.py` → revisar `TEXTO` → `narracao.py` → `tipos.py`.
- **Vídeos GRAVADOS pelo dono (`gravados-reels/`, out/2026):** ele grava falando para a câmera + cenas dos jogos, eu edito.
  Arquivo grande: ele sobe numa pasta do **Google Drive** pública e eu baixo com `pip install gdown; python3 -m gdown <link da pasta>`
  (funciona pelo proxy). Brutos ficam em `gravados-reels/brutos/` (fora do git). `criancas.py` (jogos para crianças, ~35 s):
  falas boas cortadas da tomada longa (ele erra e repete; uso a última tentativa boa), rosto dele 1,7 s e corte para as cenas
  do jogo com a fala por cima, legenda, "comenta" e CTA com mosaico das cenas dele. Pedidos dele: **qualidade de luz, som e
  edição**; imagem por cima só se for **oficial** (nunca recorte do site); o gancho é a cena dele **pertinho do celular
  ajeitando a câmera** (a ÚLTIMA aproximação do `vg.mp4`, 8,45–11,15 s) com `camera()`: aproxima 10% devagar e abre
  rápido com desfoque de movimento quando ele se afasta; depois ele fala "A gente separou quatro ótimos jogos…" e entra
  uma montagem rápida dos 4 jogos. **1ª versão REJEITADA ("áudio horrível, jogos super estourados, refaz tudo"):**
  EQ forte na voz (+5 dB de agudo, aexciter, agate) soou artificial, e normalize + curvas + vibrance estouraram os brancos
  (de ~0% para 5% de pixels ≥250) e a saturação (+60–75%). **2ª versão:** voz só com highpass 75 Hz, −2 dB em 300 Hz,
  compressão leve 2:1 e loudnorm; cor só com `eq` leve (contraste 1,03, saturação 1,05) + denoise e nitidez fracos;
  trilha mais baixa (`musica_ganho=0.2`, `duck=0.8` em `som.build`). **Lição: em vídeo gravado, mexa pouco; meça
  estouro (% ≥250) e saturação contra o bruto antes de mandar.** 39 s, com e sem legenda, 2 passadas a 5200k para o chat.
  **3ª rodada ("voz de Darth Vader", "só cortou e colou"):** a voz saía em 48 kHz e `read_wav` toca a 44,1 kHz → 9% mais
  lenta e grave e fora de sincronia. **Extraia a voz SEMPRE com `-ar 44100`.** Também havia buraco de 0,2 s entre planos
  (imagem adiantada); cortes agora por quadros exatos (`nq()`). Edição que ele pediu, por jogo: rosto dele LIVRE (nada
  escrito na frente do rosto) → a capa OFICIAL pequena no canto de baixo à direita quando ele FALA o nome (tempo do
  Whisper) → o vídeo do jogo na mesa em tela cheia com nome + fichas (tipo, jogadores, idade, tempo) → volta pra ele, ainda
  com a capa. Cada trecho de cena só UMA vez. Legenda palavra a palavra (1–3 palavras, a falada em amarelo, `palavras.json`).
  **Capas da edição ATUAL/brasileira** (ele cobrou): Go Cuckoo é a da **Devir (2023, 5+)**, foto da Bravo Jogos; Draftosaurus
  da **MeepleBR** (site da editora, wp-content); Gravity Superstar (Sit Down!) e Scooby-Doo (CMON) têm a mesma capa da dele.
  Compara Jogos (`/item/<slug>`, og:image) às vezes traz a edição estrangeira: confira contra a caixa que aparece no vídeo dele.
  **4ª rodada:** ele quer MAIS jogo na tela: o rosto dele só na apresentação (até ~0,9 s depois de dizer o nome) e daí
  até o fim da fala só as cenas do jogo (2 por jogo) + `RESPIRO` de 0,7 s antes do próximo; sem voltar pro rosto.
  Giro dele no começo do Scooby: ele disse para DEIXAR ("não ficou horrível"). **Som de microfone de lapela/sem fio dele:**
  chega muito grave/abafado e muito alto; o que soava "esquisito" era o loudnorm dinâmico bombeando e o `tanh` da
  mixagem saturando a voz. Receita: EQ moderada (−4 dB em 320 Hz, −2 em 140, +2 em 3,2 kHz, shelf +2 em 6 kHz), ganho
  FIXO por fala (`nivela`), `som.build(..., satura=False)` e loudnorm LINEAR em 2 passadas no final (`final_loudness`).
  **5ª rodada (`criancas2.py`, gravação nova em `brutos/novos/`):** gancho novo (182144) e todas as falas numa tomada
  (182216), usando a ÚLTIMA tentativa boa de cada uma (cortes conferidos transcrevendo cada pedaço). Ele: "no celular a
  100% o som explode, um pouco mais baixo fica bom" → loudness final **−15,5 LUFS com pico −2 dB**. Edição "adulta":
  sem emoji de balão no gancho; efeitos discretos do jogo por cima das cenas da mesa (`efeitos()`): ovos caindo (Go
  Cuckoo), estrelas brilhando (Gravity), pegadas subindo pela direita (Draftosaurus), névoa + fantasma (Scooby; ele pediu para TIRAR o "ZOINKS!").
  Rosto sem punch-in (o boné cortava). Final: "comenta" → ele falando o CTA ("Todos esses jogos já estão disponíveis lá
  na Sua Vez...") → tela final. 48 s.
  **6ª rodada:** (1) o gancho começa com ele JÁ mexendo na câmera (1,85 s do 182144), não indo até ela; (2) **nunca
  começar um corte na puxada de ar**: o início de cada fala é a 1ª palavra, medida pela energia (salto para > −25 dB
  depois do respiro/estalo); (3) acabamento "HD" sem estourar cor: hqdn3d forte + curva que segura os brancos (estouro
  ~5% → 0,3%) + unsharp só na luz + vinheta PI/14 + saturação 0,95–0,97 e gamma 1,04 (conferir estouro, saturação e
  brilho contra o bruto). 45 s, −15,4 LUFS, pico −3 dB.
  Vídeos gravados podem ter menos de 1 minuto.
  **Capa do Reels** (`capa_criancas.py`, pedido dele: "bem colorida, com a nossa logo"): raios coloridos + confete,
  logo, faixa "INDICAÇÃO PRO DIA DAS CRIANÇAS", "4 JOGOS" letra a letra colorida + "PRA JOGAR COM AS CRIANÇAS!" e as 4
  caixas oficiais grandes em 2x2. A 1ª versão tinha ele recortado com rembg (`u2net_human_seg`, recorte ótimo,
  `assets/capa/rosto_criancas.png`), mas ele pediu para **tirar a foto dele e deixar só os jogos em destaque**.
  Tudo dentro da área 4:5 do meio (y 285–1635), que aparece na grade do perfil.
- **Final Girl (`finalgirl-reels/`, out/2026):** ele tem a Caixa Base + a 1ª temporada (Hans, Poltergeist, Inkanyamba,
  Geppetto e **Dr. Medo**). Escolheu o **visual 2, Trailer Slasher** (`conceitos.py`): tela escura com névoa lisa, facho
  de lanterna revelando as artes (`no_escuro`), títulos em Creepster vermelho com brilho, relâmpagos, faixas de cinema e
  trilha de trailer de terror (`som_fg.py`: drone, coração que acelera, braam, trovão, stinger). Script: `trailer.py`.
  **Edição BRASILEIRA = Ludofun** (store.ludofun.com.br; fotos 1200 px em fundo branco, CDN awsli): Caixa Base, O Terror em
  Happy Trails (Hans), A Assombração da Mansão Creech (Poltergeist), Massacre nos Bosques (Inkanyamba), Carnificina no
  Circo (Geppetto) e Terror em Maple Lane (Dr. Medo). Recortes em `recortes_br.py`; a arte de cada assassino vem do
  tabuleiro oficial da Van Ryder (`FFn-compview.png`, só a arte, sem os textos em inglês) e o Hans grande do verso da caixa.
  Artes retangulares precisam de borda esfumada (`esfuma`) senão aparece o retângulo no escuro.
  **Regras conferidas** (manual/Zatu): dados = nível de Horror; 5 ou 6 = sucesso (3–4 = parcial, descartando 2 cartas);
  cada vítima morta sobe a Sede de Sangue do assassino; o Final é revelado quando o baralho do Terror acaba; vence quem
  mata o assassino. Caixa: 1 jogador, 20–60 min, 14+. Prévia mandada; gravador (arquivos `finalgirl_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/2cdb54d81a82415bb8f545a35b43ad98a6f5dea2/finalgirl-reels/gravador/Gravar_narracao_FinalGirl.html`.
  Ao receber: `narracao/raw/` → tmp_NN.wav → `tratar_narracao.py` → revisar `TEXTO` → `narracao.py` → `trailer.py`.
- **5, 4, 3, 2, 1 (`gravados-reels/lista54321.py`, 10/out/2026):** ele responde, alguém pergunta fora da câmera (o
  microfone Kaidi está preso numa espátula, de piada). Ele travou no "3" e no "1": usei a última tentativa. Respostas:
  5 = Ticket to Ride ("Chikichuride" no Whisper), Dixit, Marvel United, Trio, Flip 7 ("Flip Set"); 4 = King of Tokyo,
  The Resistance, Coup ("Koop"), boop.; 3 = Jaipur, Splendor Duel, Azul Duel; 2 = Harmonies, Azul; 1 = Hitster.
  Visual "contagem regressiva": número batendo no meio → selo do título, casas "?" que recebem as caixas quando ele
  fala o nome, no "1" a caixa sozinha com raios dourados; tudo do peito para baixo (o rosto dele fica no alto do quadro).
  Corte seco alternando aberto / punch-in 6% ancorado no topo. **Caixas oficiais BR:** a loja da Galápagos
  (`loja.galapagosjogos.com.br/ccstore/v1/search?Ntt=<nome>`, Oracle Commerce; imagem em `product.primaryFullImageURL`
  + `&height=1600&width=1600`) tem foto 3D oficial de quase tudo dela (Harmonies, Azul, Azul Duel, Splendor Duel,
  Ticket to Ride — já com a arte nova —, Dixit, Jaipur, The Resistance, Marvel United, Hitster). Flip 7 BR é da Grok
  (`loja.grokgames.com.br/flip-7`, CDN awsli 2500x2500). King of Tokyo (Devir), Coup (Funbox) e Trio (PaperGames) vieram
  do Compara Jogos. boop. não tem edição BR: a da loja é a original. Recortes: `recortes_lista.py` → `assets/lista/`.
- **"Quando tem novata na loja:" (`gravados-reels/novata.py`, 11/out/2026):** trend da referência que ele mandou
  (`brutos/perguntas/ref/`, fora do git): pergunta → chicote de câmera → o "culpado" rindo. A novata (com a Lila no colo)
  pergunta "Eric, quem mandou a novata...?" e corta pro **Eric** rindo. Pares que ELE definiu: Bananagrams (090602) →
  Eric na prateleira (090022); Uno (090724, 2ª tentativa, com chicote real no fim) → Eric em pé na mesa (090102);
  tapetes de Marrakech (091548, 2ª tentativa) → Eric andando no corredor com caixas (090212, até 3,45 s); Coffee Rush (091719) →
  Eric sentado (090311). As risadas 3 e 4 vão até ele SAIR do quadro (pedido dele: "a ideia era sair da câmera um pouco"). Gravaram em takes separados (só eles dois): a transição é um chicote digital (borrão horizontal
  + deslocamento espelhado, 6 quadros de cada lado), e onde há chicote real o corte cai no meio do borrão. Texto fixo
  "Quando tem novata na loja:" no alto, legenda só nas perguntas, tela final com as 4 caixas (Bananagrams e Coffee Rush
  da Galápagos, Marrakech da **Grok** (edição BR), Uno da Mattel pela Ri Happy, VTEX
  `rihappy.com.br/api/catalog_system/pub/products/search?ft=...`, imagem `ids/<id>-1500-1500/`). 27 s, −15,4 LUFS.
- **"Monte sua noite de jogos — TIRA PRINT!" (`roleta-reels/`, 12/out/2026):** ideia 3 da lista de conteúdos sem gravar,
  que ele escolheu. As caixas trocam rápido em 3 casas (PRA AQUECER / O JOGÃO / PRA FECHAR); cada um dá print e cai
  numa noite diferente ("a minha deu..."); fecha com "aluga os seus 3 = 7 dias". Só caixas OFICIAIS que estão no acervo
  (lista `CAIXAS` em `conceitos.py`, 24 jogos). 3 visuais mandados para ele escolher (`conceitos.py` → out/conceitos.jpg):
  1 caça-níquel neon, 2 roda da sorte, 3 cartas na mesa de feltro. Ele gostou da ideia das 3 cartas, mas não do design, e
  pediu para usar só **jogos que ainda não apareceram em post**. 2ª rodada (`conceitos2.py` → out/conceitos2.jpg): A tarô
  ("a cartomante dos jogos"), B cardápio na lousa (entrada/prato principal/sobremesa), C raspadinha. Jogos novos (todos
  no acervo, caixas oficiais em `roleta-reels/assets/`): aquecer = The Mind, Fantasy Realms, Taco Gato Cabra Queijo Pizza;
  jogão = Sheriff of Nottingham, Cartógrafos (Grok), Unicorn Fever, Sea Salt & Paper; fechar = Spyfall, Last Message,
  Happy Salmon. 7 Wonders Duel e Patchwork também recortados (só 2 jogadores, guardados para outro post). **Ele escolheu o
  TARÔ** → `roleta-reels/taro.py` (20 s): cartas chegam viradas (verso de lua), desviram e cada carta troca de jogo num
  ritmo diferente (7/6/8 quadros), quadros NÍTIDOS para o print; trilha "mística" sintetizada no script. Entregue
  `taro_{com_trilha,para_musica}_final.mp4` (−15,5 LUFS). **2ª rodada (pedido dele: "pouca opção" e "devagar"):** 22 jogos
  (7 + 8 + 7; acrescentei Splito, Flash 10, Dobro, Loser, Art Society, Bad Company, Wandering Towers, Rebirth, Eu Sou uma
  Banana, Dança dos Tronos, Perfil Express e Telma — capas do Compara Jogos conferidas contra a foto do acervo) e troca a cada
  4/3/5 quadros. **3ª rodada:** ele achou longo ("esses vídeos acabam e começam sem a pessoa perceber") → **LOOP de 7 s** com os
  mesmos 22 jogos: as cartas já começam viradas na mesa, desviram (0,25 s), giram até 6,45 s e viram de volta; "comenta" e
  "3 JOGOS = 7 DIAS · LINK NA BIO" na tela durante o giro, sem tela final; toda animação com período que fecha em DUR
  (quadro DUR·FPS idêntico ao quadro 0, conferido). **Regra para trend/print: curto e em loop.** **4ª rodada:** ele pediu para TIRAR as cartas virando
  ("ficar só uma coisa, infinita, sem parecer que tá abrindo e fechando"): cartas sempre abertas, PERIODO [4,3,6] e DUR =
  168 quadros (5,6 s), múltiplo do ciclo de cada carta (28/24/42), então o loop emenda sem pulo; só o tiquetaque no som. Depois ele notou o
  **fade out da música** no fim: `mistica()` virou trilha em loop (sem fade, frequências com ciclos inteiros em DUR,
  arpejo de passo DUR/18 com o rabo das notas somado no começo) e `som.build(..., DUR + 1e-9, ...)` para não perder a última
  amostra. **Vídeo em loop = imagem E som emendando** (conferir o último e o primeiro quadro e a amostra final × inicial). **5ª rodada:** "ainda trocando devagar" → troca a cada 2 quadros
  (15 por segundo), a carta do meio defasada 1 quadro (sempre tem alguma mudando); ciclos 14/16/14 → DUR = 224 quadros
  (7,47 s); tiquetaque a cada DUR/56. Mesmos 22 jogos.
  **Capa do Reels** (`roleta-reels/capa_taro.py`, 4/nov, "que dê curiosidade pra clicar"): A = 3 cartas de verso, a do
  meio com "?" dourado e raios ("TIRA PRINT!" / "O QUE AS CARTAS DIZEM PRA VOCÊ?"); B = visor de câmera com REC em volta
  das 3 cartas abertas ("PARA NA HORA CERTA" / "QUAL NOITE VAI SER A SUA?"). Tudo dentro de y 285–1635.
- **Conteúdo SEM GRAVAR (12/out/2026)** — ele aprovou da minha lista: 3 (roleta "tira print", esperando ele escolher o
  visual), 6, 7, 8, 9 e 11. **Dados reais do site** em `comum/dados/acervo_site.json` (161 jogos: preço por 5 dias,
  jogadores, tempo, peso; raspado de `/boardgames?page=N`) e **menor preço de loja** em `comum/dados/precos_loja.json`
  (Compara Jogos, `"lowPrice"` do JSON-LD de `/item/<slug>`). Os vídeos sem narração saem a −18 LUFS: normalizar para
  −15,5 (loudnorm linear 2 passadas, arquivos `*_final.mp4`).
  - **6 Halloween** (`halloween-reels/halloween.py`, 31 s): noite ROXA (lua, morcegos, névoa, lápides), caixa sobe da névoa
    com brilho laranja, nome em Creepster laranja, frase e jogadores/tempo. Final Girl, Scooby-Doo, Drácula vs Van
    Helsing, Tiny Epic Zombies (MeepleBR), Paranormal Detectives, DCeased (Galápagos). Ficaram de fora: Zombicide Rue
    Morgue (imagem oficial pequena) e Deep Regrets (só achei a capa em inglês). `_com_trilha` e `_para_musica`.
  - **7 "Quanto custa comprar tudo isso?"** (`custo-reels/custo.py`, 29 s): CUPOM FISCAL imprimindo; 7 jogos de R$ 30
    (Hot Streak, Ticket to Ride, Coffee Rush, Harmonies, Splendor Duel, Dixit, Marrakech) = R$ 1.616,82 nas lojas ×
    R$ 210 na Sua Vez por 15 dias (prazo progressivo), economia R$ 1.406,82. **Ele PEDIU voz de "locutor de mercado"** (aqui
    voz sintetizada vale, foi pedido dele): amostras em `custo-reels/voz/` (fora do git) com edge-tts Antonio +20–28%,
    pausas cortadas (silenceremove) e 2 mixagens: A alto-falante de mercado (dim-dom, banda 380–3600 Hz, eco, ruído de loja)
    e B locutor de rádio de ofertas (voz limpa + trilha gameshow). A voz lê mal nomes em inglês: escrever fonético.
  - Halloween: ele achou "extenso, não ficou muito legal" e não entendeu se era para narrar (era vídeo de trend, só texto).
    **2ª versão (12/out):** "mais curta" e "outros jogos, tá repetitivo; pode manter a Final Girl" → 17,8 s, 4 jogos:
    Final Girl, O Vale dos Monstros II (MS Jogos, PNG do Compara Jogos), Por favor, não corte minha cabeça! (Geeks N' Orcs,
    Compara Jogos) e Mascarade 2ª ed. (Galápagos, foto da Ri Happy); sem numeração "n/6". Zombicide Rue Morgue segue sem
    imagem oficial boa (Compara Jogos só 322 px). Unmatched Robin Hood: só achei a capa em inglês (a da loja é a da Buró).
  - **Custo:** ele recusou as 2 vozes de locutor ("não gostei de nenhum dos áudios, pode deixar sem"): fica sem voz. 2ª versão
    mais rápida (ele: "um pouquinho demorado"): 29 s → 20 s (GANCHO 1,7, 1,1 s por jogo, caixa quicando em 0,35 s).
    3ª versão: ele sentiu falta de um **lado a lado** ("não pague 1.600, pague 200 e jogue 15 dias"): cena `cena_lado`
    depois do cupom da Sua Vez (SEM título: ele achou estranho o "LADO A LADO" escrito): cartões COMPRAR (vermelho, R$ 1.616,82 riscado) × ALUGAR (verde, R$ 210, 15 dias), os
    mesmos 7 jogos em miniatura nos dois, "VS", e "NÃO PAGUE R$ 1.616 / PAGUE R$ 210 E JOGUE 15 DIAS!". 23,8 s.
  - **Halloween, 3ª rodada:** ele achou a noite roxa (lua, morcegos, abóbora) "muito infantil" e pediu para mudar TODO o
    visual. Mandei 3 conceitos adultos (`halloween-reels/conceitos.py` → out/conceitos.jpg; fontes Cinzel e Cormorant
    Garamond do google/fonts em `assets/fonts/`): 1 pôster de cinema (preto, luz fria, letreiro serifado espaçado,
    créditos), 2 mansão gótica (retrato em moldura dourada, velas, placa de museu), 3 tabuleiro Ouija (prancheta soletra
    o nome). **Ele escolheu o PÔSTER DE CINEMA** → `halloween-reels/poster.py` (18,8 s): gancho "A SUA VEZ APRESENTA /
    QUATRO JOGOS PARA NÃO DORMIR / Você tem coragem?"; cada jogo = lâmpada que acende piscando + facho frio, caixa
    aproximando 4%, título Cinzel com as letras se juntando, frase em Cormorant itálico e créditos; some no escuro entre
    pôsteres; "QUAL VOCÊ ENCARA PRIMEIRO? / Comenta aqui."; final "EM CARTAZ NA SUA VEZ". `halloween.py` (roxo) ficou
    como versão rejeitada.
  - **Carrosséis 1080x1080** (`feed-posts/carrosseis.py`, visual creme + círculo colorido, cores do site): "O jogo certo
    pra cada rolê" (8 telas), "Curte esse clássico?" (7: UNO→Flip 7 A Vingança, Scrabble→Bananagrams, Imagem &
    Ação→Dixit, Detetive→MicroMacro Full House, Jogo da Velha→boop.; Root saiu porque a da loja é a edição em inglês) e
    **"Top 5 queridinhos da Sua Vez"** (7). Ele pediu "top 5 mais alugados do mês" e disse para inventar porque ainda não
    houve aluguéis; **não inventei número de aluguel**: virou "os que a gente mais indica", com as frases dele no 5-4-3-2-1
    (King of Tokyo, Ticket to Ride, Splendor Duel, Harmonies, Hitster; Azul não está no acervo).
  - **2ª versão dos carrosséis** (`feed-posts/carrosseis2.py`, ele: "todos iguais" e "jogos repetidos, quase todos têm o
    Hitster / Ticket to Ride"): **cada um com layout próprio** e **nenhum jogo repetido** entre eles nem com posts anteriores.
    Rolê = print de conversa de WhatsApp (Patchwork, Monkey Palace, Say my Name, Survive the Island, Santa Kaos,
    Dinosaur World; emoji desenhado como imagem porque a Poppins não tem emoji); Clássicos = antes × depois em papel
    envelhecido (UNO→Flip 7 A Vingança, Detetive→MicroMacro, Batalha Naval→Mind MGMT, War→Wonderland's War);
    Top 5 = ranking de revista (Jungo, Bandido, Next Station London, Dungeon Fighter, Take Time — escolha minha, ele pode
    trocar). **Regra que fica: variar jogos entre posts** (ver o que já foi usado antes de escolher). Pedidos seguintes: **sem
    numeração "1/7" nas imagens** (ele achou que era coisa do chat) e, nos clássicos, **a caixa do clássico também** (menor,
    com tom envelhecido, no "antes"; UNO Mattel, Detetive Estrela, Batalha Naval e War Grow, fotos da Ri Happy).
- **Story do Dia das Crianças** (`promo/story_criancas.py`, 12/out). v1 (céu azul, meeples desenhados em vetor) REJEITADA:
  "muito ruim, nada a ver com o visual da loja, meeples mal feitos". v2 (4 caixas em cartões) REJEITADA: "você fez uma
  imagem promocional; eu quero só o Feliz Dia das Crianças". **Lições:** (1) arte da loja segue o visual das promoções
  (`promo_3jogos.fundo`: creme com listras laranja, cartão branco do logo, Poppins azul-marinho, laranja, verde, azul);
  (2) nunca desenhar meeple/peça à mão; (3) data comemorativa = FELICITAÇÃO, sem divulgar jogos (só um empurrão discreto
  pro site). v3: balões e confete nas cores da marca, "FELIZ DIA DAS / CRIANÇAS!" (faixa laranja), "Pra criança que tem
  em casa e pra que mora dentro da gente. / Hoje o dia é de brincar junto!", 4 dados geométricos e o site numa pílula.
- **Cupons:** JOGAMAUA5 (evento Joga Mauá, 5% na locação) e **JOGAABC5 = 5% de desconto para quem mora no ABC** ("Joga ABC 5";
  eu tinha escrito JOGABC5 e ele corrigiu) (12/out). Story `promo/story_cupom_abc.py`: visual da loja, "MORA NO ABC? / 5% OFF / na locação dos seus jogos!",
  ticket com o cupom, selo "VÁLIDO ATÉ 15/10", "Reserve pelo link:" + seta e espaço livre (y ~1510–1610) para o adesivo de link do Instagram.
  **Últimas horas** (`promo/story_cupom_abc_ultimas.py`, 15/out à noite): "ÚLTIMAS HORAS!" + relógio, faixa vermelha
  "O CUPOM ACABA HOJE!", ticket JOGAABC5, "VÁLIDO SÓ ATÉ HOJE, 15/10" e espaço do adesivo de link (y ~1580–1640).
- **Assinaturas (`assinatura-reels/`, 13/out, pedido da Jéssica):** `carrossel.py` (6 telas 1080x1350: capa, como funciona,
  Silver, Gold, Platinum, assine), `story.py` (1080x1920, planos empilhados + espaço para o adesivo de link) e `video.py`
  (Reels 32 s, sem narração, com e sem trilha). Caixas OFICIAIS por categoria em `estilo.JOGOS`. Não inventei "plano mais
  pedido" (é lançamento). Pus a nota "na entrega, a taxa varia conforme a região e é cobrada a cada troca" (o Erik já
  pediu para não citar taxa nas artes; avisei a Jéssica para decidir).
- **Carrosséis estão indo bem (14/out):** pediram mais. `feed-sua-vez/porque_alugar.py` (7 telas 1080x1350, identidade
  da Jéssica): capa, 5 motivos (jogo moderno é caro: Critter Kitchen R$ 283, Victorian Masterminds R$ 258, Everdell Duo
  R$ 225 × R$ 30, menor preço Compara Jogos 14/10; teste antes de comprar; 163 jogos; nada parado na estante; 3/5/7 jogos
  = 7/10/15 dias ou assinatura a partir de R$ 49) e chamada. **Monitoria em eventos** (`feed-sua-vez/eventos.py`, 6 telas): eles
  levam os jogos e ficam o evento TODO ensinando/ajudando; qualquer tipo de evento; quantidade de jogos conforme nº e
  perfil de pessoas; duração = do evento; atendem principalmente o ABC Paulista; jogos para crianças e adultos, agitados e
  tranquilos; preço só por orçamento (Direct ou WhatsApp; número do WhatsApp ainda não informado → "WhatsApp do link na
  bio"). **Ainda não fizeram nenhum evento:** sem fotos reais, sem "já atendemos", sem depoimentos. **Pedido de 14/out: variar o fundo entre os carrosséis**
  (estava tudo azul-claro): mesma identidade (fontes, contorno marrom, sombra, selos), fundo diferente por post —
  assinatura = azul-claro com trilha (`fundo`), Por que alugar = amarelo xadrez (`fundo_xadrez`), Eventos = ROXO (108,63,160; ele pediu
  roxo no lugar do laranja) com confete só nas bordas (`fundo_confete`, `livre=`, `base=`), textos sobre o roxo em branco. **Depois ele disse "tá copia e cola, só mudou o fundo; quero
  mais diverso":** cada carrossel ganhou um CONCEITO de layout próprio, mantendo só fontes/cores/contorno: Por que alugar
  = "cartas na manga" (cada motivo é uma carta de baralho gigante com índice no canto, baralho atrás, capa com leque de
  cartas viradas); Eventos = "convite de festa" (envelope com convite, programação pontilhada, cartõezinhos só com o nome do
  evento (ele não gostou dos BALÕES nem do "Olá! meu evento é…"; "Empresarial", não "Empresa"), cardápio da festa, ficha de RSVP com carimbo "ABC Paulista", ingresso destacável). **Regra: carrossel novo =
  conceito novo**, não só cor nova. Cuidar do contraste: nada amarelo sobre amarelo nem laranja sobre laranja.
- **Eventos em 1x1 (15/out):** ele pediu o carrossel da monitoria QUADRADO para o post: `feed-sua-vez/eventos_1x1.py`
  (cópia do eventos.py com W,H = 1080x1080, peças reposicionadas e cartões a 85–88%) → `out/eventos_1x1/01..06.png`.
- **"Como alugar no site" (`feed-sua-vez/como_alugar.py`, 14/out, pedido da Jéssica; + assinatura a pedido dela):**
  conceito TUTORIAL DE CELULAR: fundo petróleo pontilhado, trilha amarela tracejada passando de uma tela pra outra, selo
  redondo com o nº do passo, celular grande saindo pela borda com a tela do site REDESENHADA a partir das telas reais
  (Playwright: `pip install playwright==1.56.0` casa com o Chromium de /opt/pw-browsers; `launch(proxy={'server':
  $HTTPS_PROXY})` e `goto(..., wait_until='commit')` + espera; o proxy falha às vezes, então repita) e um dedo tocando o
  botão. Fluxo real: acervo (busca + filtros) → página do jogo "Alugar" → carrinho ("Com 3 jogos, você ganhou prazo extra:
  todos ficam 7 dias sem pagar nada a mais.", itens "R$ 30 por 7 dias", "Entrar para finalizar", "Frete combinado na
  próxima etapa.") → "Login de clientes" / "Criar conta" (cadastro pede nome, email, CPF, RG, celular, endereço) →
  finalizar (NÃO vi o checkout: precisa de conta; o passo 5 só diz retirada em Mauá ou entrega, frete combinado, Pix ou
  cartão). **Assinatura no site:** página Planos com "Assinar pelo WhatsApp", que abre o wa.me com "Olá! Quero assinar o
  plano Assinatura <Silver/Gold/Platinum>." **WhatsApp da loja: (11) 97793-3910** (está no rodapé do site; serve para o
  carrossel de eventos). **Ajustes pedidos:** usar as FOTOS DO SITE (render no fundo laranja, `feed-sua-vez/assets/site/`, cópia de `hobby-reels/assets/acervo_foto/`; a do The Resistance tem a estrelinha do gerador no canto, cortada) em vez das caixas recortadas; **não pôr o endereço da loja**; foto NUNCA cortada: em área não quadrada ela entra inteira e as sobras viram a própria foto desfocada (`recorte_foto`; ele reclamou do Azul Duel cortado na página do jogo); tela final reta e centralizada (a 1ª, com título e cartão girados em sentidos opostos, ficou "desalinhada"). Dá pra adicionar ao carrinho sem conta com curl (form POST `/cart/items?boardgame_id=` + token).
  **Vídeo (`feed-sua-vez/como_alugar_video.py`, 14/out):** Reels 1080x1920 ~36 s com as MESMAS telas animadas (tela desliza
  dentro do celular, mão entra e toca com onda + som, dica em pílula embaixo), passos 1–5 + assinatura (Planos → WhatsApp) + CTA;
  sem narração; `_com_trilha`/`_para_musica` → `*_final.mp4` (loudnorm linear 2 passadas, −15,5 LUFS).
- **"Avaliando os jogos que jogamos essa semana" (`feed-sua-vez/semana.py`, 14/out):** trend do TikTok; ELE dá as notas e
  as frases (nunca inventar). Rejeitou os 3 visuais de `conceitos_semana.py` (caderno, trilha de pontos, medidor) e pediu
  "só o jogo na mesa e a escrita": mesa de madeira em numpy + fotos OFICIAIS dos componentes pousadas com sombra (não
  há fotos das partidas) + texto branco com sombra (nome, nota amarela, frase). **Fotos de componentes:** a API da
  Galápagos dá todas as fotos do produto: `ccstore/v1/products/<ID>` → `fullImageURLs` (+ `&height=2000&width=2000`);
  IDs: SPL201 Splendor Duel, HIT003 Hitster Lado B, TTR401 Ticket to Ride Legacy: Lendas do Oeste. PaperGames
  (wp-content) tem as cartas do Trio uma a uma. Foto em fundo branco: branco ligado à borda vira transparente e a sombra
  do estúdio entra MULTIPLICADA na madeira (`semana.produto/pousa`). 1ª rodada: TTR Legacy 10, Splendor Duel 8 ("minha
  esposa ficou bem brava ontem... mas eu ganhei!"), Hitster Lado B 10, Trio 9. TTR Legacy e Trio NÃO estão no acervo.
- **3º antigo × moderno (`feed-posts/classicos3.py`, 14/out):** mandei 3 visuais novos (`feed-sua-vez/conceitos_classicos.py`:
  evoluiu, deu match, TV antiga) e ele disse: **"nesse tema a gente mantém o MESMO design"** (o antes × depois de
  `carrosseis2.py`, 1080x1080; o script novo importa as funções de lá). Pares: Ludo → Camel Up, Xadrez → Hive, Stop →
  Tapalavras, Banco Imobiliário (retrô, Estrela) → Bohnanza, Lince (Grow) → Spot it! Hip, e os 2 extras que ele pediu:
  Truco (baralho Copag 139) → Coup, Super Trunfo (Grow) → 1, 2, 3, Lucha! Clássicos: Ri Happy VTEX recortados (caixa
  branca = flood fill + casco convexo do maior pedaço); modernos: recortes do site em `hobby-reels/assets/acervo/`; a lata do
  Spot it saiu de `recortes_caixas.recorta` + remoção do laranja ligado ao fundo.
  **Versão final (escolha dele, 14/out): só 4 pares** — Ludo → Camel Up, Xadrez → Hive, Stop → Tapalavras e Jogo da Memória
  (Super Memória Grow) → ~~Uga Buga~~ **Trio** (ele trocou; o Trio NÃO está no site, ficha da PaperGames: 2 a 6 jogadores,
  15 min; caixa 3D da PaperGames em `feed-posts/assets/trio.png`) (6 telas). Os outros pares ficaram de fora.
  **15/out — ele "resetou" a lista; versão atual (6 telas):** Lince → Spot it! Hip, Imagem & Ação (Grow) → Say my Name, Xadrez → Hive (ele pediu de volta)
  (Buró; era o "da Buró parecido com Imagem & Ação") e Scotland Yard (Grow, "O jogo do Sherlock Holmes") → Convidados
  Indesejados 1 E 2 na MESMA imagem (`moderno()` junta as duas caixas). Convidados = Awkward Guests da Across the Board,
  NÃO está no site: caixa do 1 do Compara Jogos (PNG transparente), do 2 só a da loja da editora (400 px; a do Compara é
  a edição em inglês); ficha: 1 a 8 jogadores, o 2 é para duplas. Ele não quis nenhuma opção para o Banco Imobiliário
  (High Society, Bohnanza, Istanbul, Architectura) e pediu Dobble Disney para o Lince, mas NÃO está no site → ficou o Spot it.
- **Descrições do site NÃO são confiáveis (14/out):** algumas fichas têm a descrição de OUTRO jogo ("Shimp" descreve
  "Faces!", "Color Addict" descreve "Cores Confusas", "DANY" descreve "Fragmentos da Mente"). Eu usei esses nomes numa lista
  e ele disse "tem jogos aí que a gente nem tem". **Sempre conferir o jogo pela FOTO do site** (`hobby-reels/assets/acervo_foto/`)
  e mandar a lista com as fotos (`feed-sua-vez/out/lista_classicos.jpg`) ANTES de montar. Ele também pediu: **mostrar as
  opções antes de fazer** (eu montei `classicos3.py` sem ele escolher; ele reclamou).
- **Stories gravados (`gravados-reels/stories.py`, 14/out):** 2 vídeos dele para STORIES (brutos `20261014_095354` e
  `_095443` na pasta de brutos do Drive → `brutos/stories/`, fora do git). Pedido: "editada básica e legenda": corte do
  silêncio inicial (0,45 s), 1080x1920, GRADE_ROSTO leve, EQ do microfone de lapela, legenda palavra a palavra em y≈1400,
  −15,5 LUFS; sem trilha/logo/tela final. Whisper corrigido: "Wonder Towers" → Wandering Towers, "no set" → no site,
  "joga BC5" → JOGAABC5, "alocação" → locação, "próximo source" → próximo story. Saída `out/story{1,2}_{legendado,sem_legenda}.mp4`.
- **Comparativo "o que ele citou × site" (15/out):** o site tem **164** jogos (entraram Marvel United: Multiverse, Trial by
  Trolley e **Trio**). Citados por eles e AUSENTES do site: Ticket to Ride Legacy: Lendas do Oeste, Dobble Disney,
  Convidados Indesejados 1 e 2, Jaipur, Azul (só tem o Azul Duel), Vudú, Sintonia e as 5 expansões do Final Girl (só há
  "Final Girl"). Nome diferente da caixa: "Coup: Inquisition" (a foto é o Coup 2ª ed. com A Reforma) e "Flip 7: A Vingança"
  (no 5-4-3-2-1 ele disse Flip 7). `comum/dados/acervo_site.json` ainda tem os 161 de 12/out.
- **"Quanto você conhece o outro?" (16/out, ideia dele):** Erik e Jéssica respondem as mesmas perguntas sem ouvir a
  resposta do outro ("eu acho que o favorito dela é X, e o meu é Y"). Mandei 15 perguntas, ele achou muito → ficaram 6 (favorito, joga melhor, deu briga, pior desculpa ao perder, mais competitivo, primeiro jogo juntos). Sugeri gravar
  cada um SEPARADO (mesma luz, mesmo enquadramento), para eu montar em tela dividida com o placar de acertos. **16/out:** subiram 2 arquivos `20261016_154151.mp4` no Drive de brutos, mas são IDÊNTICOS (mesmo md5) = só o da Jéssica (1:39, segurando o UNO Stacko como microfone; em `brutos/casal/casal.mp4` + `palavras.json`). Ela respondeu 5 (sem "primeiro jogo"): favorito dela Clank, dele Ticket to Ride; ela joga melhor Sea Salt & Paper, ele Wingspan; briga feia = The Resistance; desculpa dele = "ela roubou"; competitivo = "todos, todos" (~75–81 s, ZOOM no rosto dela, pedido dela). Pedidos: correção leve de luz e de áudio. **Editado em `gravados-reels/casal.py`** (16/out): brutos certos `erik.mp4` (153506, 3:11; ele lê
  as perguntas) e `jess.mp4` (171307, 2ª gravação dela, 1:19). Respostas dele: favorito Wingspan, acha que o dela é Harmonies; ele
  melhor em Ticket to Ride, ela em Clank Catacombs ("Tio Patinhas"); briga = The Resistance ("menti tanto que levei um tapa na
  cara"); desculpa dela = "não ensinei tudo", a dele = ela é Tio Patinhas; competitivo: ela Drácula vs Van Helsing, ele Cat in the
  Box; 1º jogo juntos Scotland Yard (1º moderno Dixit). Dela: Clank / Ticket to Ride; Sea Salt & Paper / Wingspan; The Resistance;
  "o outro roubou, é clássico"; ela Ticket to Ride, ele "todos, todos"; Dixit. Placar 1 de 6 (+ "quase" no 6). Montagem: teaser do
  tapa → pergunta escrita num painel escuro (a leitura dele em voz alta saiu, pra encurtar) → ERIK → JÉSSICA → carimbo BATEU/NÃO
  BATEU/QUASE (quadro congelado 0,9 s, ding/buzz) → placar → "E vocês? marca o seu par" → tela final com 8 caixas. Pausas > 0,3 s
  viram corte seco (energia), alternando punch-in 7%. Zoom 1,42 no "todos... todos." (bruto 63,3 s). Luz: ele segura os brancos,
  ela sobe os médios. ~103 s. **2ª rodada (pedido dele):** só a versão COM legenda; teaser do tapa em PRETO E BRANCO ("bastidores") e o
  tapa REPETE em cores na pergunta 3 (ele quer: o começo instiga, o meio dá o contexto); na pergunta 1 ela fala "o meu jogo favorito é..." DUAS vezes → só a 2ª (16,75 s);
  o "todos, todos" dela perdia o 1º "todos" num corte → trecho marcado "inteiro" (sem corte interno); pedacinhos sem palavra
  saem. **Caixa do jogo citado** aparece ao lado quando o nome é dito (`CITA`, índice da palavra; 905,760, até 2,6 s): Cat in
  the Box = Galápagos CBX001 (`assets/casal/`), Scotland Yard = foto da Grow; o "Clank" dela = Clank! base (ela não disse qual).
  Trilha gameshow: ele pediu MAIS alta (estava inaudível) → musica_ganho 0.24, duck 0.55 (~11 dB abaixo da voz).
  **Para conferir cortes:** transcrever a faixa `out/casal_voz.wav` montada e listar o texto de cada plano (achou os 2 erros).
- **Santorini (`santorini-reels/`, 16/out, começando):** no site: R$ 30, 2–4 jogadores, 20 min. A foto do site é a edição
  Spin Master 2024 ("Build like a mortal..."); a Roxley (Shopify `roxley.com/products/santorini.json`, imagens oficiais 1284 px
  em `assets/orig/`, fora do git) tem a Pantheon/2ª ed.; no clipe dele (`byebye-reels/referencia/clipes/c3.mp4`) há torres
  brancas, cúpulas azuis e construtores cinza. **A caixa deles é a do SITE (Spin Master 2024): usar `hobby-reels/assets/acervo/santorini.png` (recorte da foto do site), NÃO as da Roxley.** Perguntei se podem filmar as peças (≈10 clipes: mover,
  construir 1-2-3-cúpula, subir no 3º = vitória, cartas de deus). **Ele NÃO consegue filmar** → tudo desenhado: `ilha.py` (ilha isométrica 5x5 em PIL: andares cada vez mais estreitos, cúpula azul, peão desenhado) e `conceitos.py` → out/conceitos.jpg com 3 visuais: 1 maquete ao sol, 2 pôr do sol épico (Cinzel dourado "Construa como um mortal / Vença como um deus"), 3 vista de cima (manual animado). **Ele escolheu o PÔR DO SOL mas NÃO gostou das peças desenhadas: quer FOTOS do jogo.**
  Fotos oficiais da edição dele (Spin Master) na **Zatu** (Shopify `zatu.com/products/santorini-spinmaster.json`, 4320 px, fundo
  branco): caixa 3D, tabuleiro montado com torres + leque de cartas de deus, verso. Recortes em `assets/fotos/zatu_{1,2,3}.png`.
  O manual oficial Spin Master (PDF no Salsify, `assets/orig/sm/manual_sm.pdf`) tem blocos/cúpula/peões/deuses, mas as imagens
  são PEQUENAS (70–400 px): não servem para vídeo. `conceitos2.py` → out/conceitos2.jpg: gancho (tabuleiro da foto no mar ao
  pôr do sol), regra (o clipe c3 deles com luz dourada), deuses (leque de cartas da foto). Ele perguntou "não dá pra fazer que nem o Vudú/Arquitetos?" → **STOP MOTION com as peças
  OFICIAIS do manual**: os renders 3D do manual (andar 1 `p1_768`, 2 `p1_788`, 3 `p1_804`, cúpula `p1_820`, construtor azul
  `p1_796`, cinza `p1_639`) ampliados 4x por IA (`ampliar.py`, Real-ESRGAN x4 em ONNX/CPU, modelo huggingface
  Meeperomi/RealESRGAN_x4-onnx no scratchpad) → `assets/pecas/`. Ficam limpos e todos no MESMO ângulo. `cena.py` monta a cena:
  perspectiva medida na base do andar 1 (A=(−125,−72), B=(220,−32) px), empilhamento pelo diagrama "A Complete Tower" do manual
  (pt × 5,6), tabuleiro 5x5 de grama com linhas brancas desenhado na mesma perspectiva (o do manual tinha peões e não limpou
  bem com inpaint). Teste: `out/teste_stopmotion.jpg` (pôr do sol, luz quente nas peças). Esperando o ok dele. Regras conferidas:
  2 construtores; move 1 casa (sobe no máx. 1 andar, desce quanto quiser) e o MESMO constrói 1 nível vizinho; cúpula fecha;
  vence quem SOBE ao 3º andar; perde quem não consegue mover+construir; deuses quebram uma regra (Apolo troca, Atlas cúpula
  em qualquer nível).
  **Vídeo: `santorini-reels/stopmo.py`** (12 fps, 66 s, 9 cenas, pôr do sol + Cinzel dourado; peças com `luz_quente`):
  torre subindo, construtores caindo na ilha, casas vizinhas acendendo (✘ vermelho ao tentar subir 2), construção 1º/2º/3º,
  cúpula 🔒, vitória no 3º com raios, leque de deuses da foto Zatu + Apolo troca + Atlas (cúpula no 1º andar, assentada em
  `cena.poe_torre`), "comenta" e tela final com a caixa do SITE. Trilha grega sintetizada em `trilha()` (ré menor harmônica;
  `note()` próprio, o do Vudú não tem E/C#). Prévia mandada; gravador (arquivos `santorini_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/fc98b46522d4074edb11fa46d5aaafd4c4ffd516/santorini-reels/gravador/Gravar_narracao_Santorini.html`.
  Ao receber: `narracao/raw/` → tmp_NN.wav → `tratar_narracao.py` → revisar `TEXTO` → `narracao.py` → `stopmo.py`.
- **"Gosta de ___? Precisa conhecer ___" (17/out, ideia dele; ELE GRAVA):** mandei 16 pares do acervo (foto do site):
  cozinhar→Critter Kitchen, pintar→Canvas, série policial→Detective, escape room→Unlock!, Jurassic Park→Dinosaur Island,
  bar→Dungeons & Drinks, fazendinha→La Granja, metrô→Next Station London, comida japonesa→Sushi Go!, trilha/mapas→
  Cartógrafos, luta livre→1,2,3 Lucha!, gatos→boop., viajar→Passaporte Mundo, leilão→High Society, arte→Art Society,
  feira→Bohnanza. **Ele escolheu 6:** Critter Kitchen, Canvas, Unlock!, Sushi Go!, Passaporte Mundo (trivia
  COOPERATIVO de países, 1–6) e Art Society (leilão secreto de quadros; o que ninguém compra vai pro museu e valoriza a
  categoria). Roteiro v2 mandado (comida → arte → viagem → escape room); esperando a gravação (edição tipo `gravados-reels/`).
- **5 vídeos SEM GRAVAR (17/out, ele escolheu da minha lista): 4 signos, 5 quanto tempo, 6 quantas pessoas, 8 red/green
  flag, 9 chegou no acervo.** Listas com fotos do site em `listas-reels/opcoes.py` → out/opcoes_*.jpg (mandadas para ele
  aprovar; nenhum jogo repetido entre os vídeos). Novos no site (17/out): Convidados Indesejados (1–8, 75 min, R$ 30),
  Marvel United: Multiverse (1–5, 40 min, R$ 30), Trial by Trolley (3–13, 90 min, R$ 30), Trio (Pocket R$ 15, 3–6, 15 min);
  fotos 1024 px baixadas para `hobby-reels/assets/acervo_foto/` (a variante 1024 do active_storage tem `ABGkCAAQ` na URL).
  **Feitos e mandados (17/out), em `listas-reels/`** (base comum `base.py`: `foto()` = FOTO DO SITE inteira num cartão,
  nunca cortada; `texto()`; `entrega()` grava _com_trilha e _para_musica e normaliza para −15,5 LUFS → `*_final.mp4`):
  `signos.py` (31 s, céu estrelado, símbolos ♈–♓ da DejaVuSans em dourado, Cinzel, grade final dos 12, trilha "mistica"
  do taro), `tempo.py` (21 s, identidade da Jéssica, despertador com ponteiro e fatia colorida, "a noite toda" escurece o
  fundo), `pessoas.py` (24 s, mesa de feltro vista de cima em piso de tábuas, cadeiras chegando 1/2/4/6/10, Alfa Slab),
  `flags.py` (28 s, fundo escuro vermelho/verde com cortina diagonal, bandeira tremulando, cartão de papel; frases dele),
  `novidades.py` (23 s, caixa de papelão que abre e o jogo sobe de dentro, confete, "Qual você aluga primeiro?").
  Signos: ele GOSTOU, mas acha que fica melhor GRAVADO por ele (mandei roteiro de gravação com as mesmas 12 frases;
  na edição dá pra reaproveitar o céu/símbolos/grade de `signos.py` por cima das cenas dele).
- **2 vídeos GRAVADOS em 17/out (brutos `gravados-reels/brutos/out17/`, fora do git):**
  - `gravados-reels/esse_aquele.py` ("ESSE OU AQUELE? versão Jéssica", 133042, 58 s): o Erik filma e pergunta, ela
    responde, quem ganha FICA. Fotos do SITE em duelo no pé da tela (vencedor brilha com coroa, perdedor leva X e cai),
    campeão Clank! Catacombs, "E você, ficava com qual?", tela final com os 12. Ganho fixo separado para a pergunta (ele) e
    a resposta (ela). Whisper: "Espírito" virou **Splito** (CONFERIR com eles), "Necoagima" = Nekojima, "Comodados
    Edejejados" = Convidados Indesejados. Saiu o "Clank Catacombs?"/"Clank." (só confirmação). 2 passadas a 3700k = 28 MB.
    **2ª rodada (pedido dele):** começa com ele CHEGANDO nela ("Amor, vamos fazer um esse ou aquele?" = gancho), saiu a
    última pergunta (Nekojima repetido), legenda palavra a palavra acima dos cartões. **3ª:** "tá dando spoiler": o cartão
    acendia antes da resposta (Whisper adianta até 0,7 s) → a reação agora sai do INÍCIO REAL da voz dela (energia, depois do
    silêncio que segue a pergunta) + 0,35 s; a legenda da resposta também espera a voz. **Regra: reveal pela energia, não pelo Whisper.**
  - `gravados-reels/indica.py` ("Me diz o que você gosta de fazer que eu te indico um jogo", 133810 + cenas 134947 Art
    Society, 135233 Passaporte, 135550 Critter, 135716 Canvas, 140020 Unlock): última tentativa boa de cada fala, MENOS o
    Canvas (a última tem 3 s estranhos no "artística"; usei 114,4–121,5). Cena do Sushi Go veio depois (140828). O
    microfone dele CORTA o silêncio (−89 dB): o Whisper adianta o começo das falas ~0,6 s, então a legenda pega palavra
    que SOBREPÕE o plano. 58 s.
- **Trial by Trolley com os STORIES dele (`gravados-reels/trolley.py`, 17/out):** 4 stories de 14/out mandados pelo chat
  (720x1280 do Instagram; brutos em `brutos/stories1014/`, fora do git): rosto → caixa na estante → explicação na mesa
  (2 trilhos, inocentes/culpado/modificadores) → enquete. Saiu o que era de story ("vai entrar no site essa semana",
  "no próximo story / votação"); a enquete virou "POR ONDE O BONDINHO PASSA? DE CIMA / DE BAIXO · Comenta aqui!".
  Textos das cartas lidos nos quadros para corrigir o Whisper (freiras se divertindo, abelhas, terças-feiras). Fala +
  imagem a 1,1x (`VEL`) para caber; 1:22. 720p → 1080p com lanczos + nitidez leve. **2ª rodada:** o fim "vou deixar vocês
  decidirem" cortava seco → emenda direto no 4º story (a mesa montada, zoom lento) com "E AÍ, VOCÊ DECIDE!", rótulos
  TRILHO DE CIMA / DE BAIXO e a placa da pergunta COBRINDO a enquete gravada; cortes alternando aberto / punch-in 7%.
- **Take Time "em 1 minuto ou menos" (`gravados-reels/taketime.py`, 18/out):** 5 vídeos de story dele no Drive de brutos
  (`brutos/out18/`, fora do git; 153426 e 153528 são cópias de 153358 e 153455): gancho no espelho ("Eu vou explicar o
  Take Time em 1 minuto ou menos"; o Whisper ouviu "o time"), caixa, baralho sol/lua e capas, a regra na mesa com o relógio,
  fecho "a gente joga em casal... corre lá!". Conceito CONTRA O RELÓGIO: relógio no estilo do jogo (mostrador lilás, aro
  dourado, 6 seções, sombra que gira) conta de 1:00 a 0 durante a explicação (fica vermelho e pulsa nos últimos 10 s),
  selos das regras na hora da palavra, carimbo "EXPLICADO EM 59 SEGUNDOS!". Explicação a 1,2x (`VEL_EXP`) para caber em
  60 s; o 153134 tem só o gancho de útil (o resto é o celular balançando). "Comenta": "Jogo cooperativo: une ou separa o casal?".
  Site: 2–4 jogadores, 30 min, R$ 30. ~81 s. **2ª rodada:** saiu o "E... claro," hesitado antes do "ele já está no site"; a
  última frase ("...são 12 capas") a 1,1x com fade de 0,12 s e RESPIRO de 0,35 s antes do carimbo (o bruto acaba colado no
  "capas", limite de 60 s do story; a 1,2x e com o ding em cima parecia cortar a letra). **3ª rodada:** medido no bruto,
  o "s" de "capas" NÃO foi gravado (nada agudo depois de 59,92 s): emendei o "s" do "cartas." dele (44,76–44,92 s, −8 dB)
  logo depois do "capa", e a última frase foi para 1,0x (a 1,1x o "p" borrava). Não use o Whisper como juiz de enxerto: sem
  o "s" ele "completa" para capas pelo contexto e com o "s" ouve "casas". O fecho do casal também a 1,2x (pedido dele: "na
  mesma velocidade do resto"). ~80 s. **4ª rodada:** a explicação (e o relógio) termina no "...a gente segue para o
  próximo." (56 s → "EXPLICADO EM 56 SEGUNDOS!", relógio para em 0:04); "Dentro de cada capa tem 4 relógios... 12 capas" já é
  o fecho, junto com o casal. Pausa de 0,9 s depois do "próximo" com a imagem seguindo e a voz/legenda em SILÊNCIO (`nv` =
  quadros com voz; antes a pausa lia o áudio do bruto e o "Dentro" saía duas vezes).
- **"Vem separar 2 pedidos comigo" (`gravados-reels/pedidos.py`, 19/out, Jéssica):** brutos `brutos/out19/` (fora do
  git): 102837 = ela na estante ("Bom dia! Vem separar dois pedidos comigo!"), 103147 = a câmera dela pegando os jogos e
  pondo em DUAS cadeiras (sem fala; vídeos com rotação oposta, o ffmpeg desgira sozinho). Pedido 1 (cadeira esquerda):
  Canvas (identificado por ORB contra as fotos do site), La Granja, Convidados Indesejados; pedido 2: Throw Throw Burrito,
  Echoes of Time, Azul Duel — 3 jogos cada = 7 dias. Edição: rampas de velocidade (procura 3x, pegar/mostrar 1,25x — ele
  pediu "acelerar só um pouquinho na parte de mostrar os jogos" —, pôr na cadeira 1,5x), cartão com nome + ficha do site,
  lista do pedido no canto com ✓ quando o jogo assenta, selo "3 JOGOS = 7 DIAS!", "PEDIDO 2!", "PEDIDOS PRONTOS!",
  "Qual pedido você levaria? Comenta 1 ou 2!" e tela final com as 6 fotos do site. Trilha travessa. ~45 s.
- **Capa do "Quanto a gente se conhece?" (`gravados-reels/capa_casal.py`, 19/out, pedido da Jéssica):** 1080x1920, o
  que importa na área da grade (y 285–1635). A = tela dividida na DIAGONAL com os quadros inteiros (ela 36,4 s sorrisinho à
  esquerda, ele 155,8 s olhando de lado PARA ela à direita), título "QUANTO A GENTE SE CONHECE?", ELA/ELE, VS e "SERÁ QUE A
  GENTE ACERTA?"; B = dois quadros como fotos inclinadas (ela 49,8 s, ele 112,9 s) no azul-claro listrado + "ACERTAMOS SÓ
  1 DE 6?!". O recorte por rembg ficou com bordas RETAS onde a pessoa encosta na borda do quadro (cabelo no topo) →
  para rosto colado na borda, use o quadro inteiro, não o recorte. **2ª rodada:** ela NÃO gostou dos takes ("sorrindo e
  olhando pra câmera, não olhando pros lados") → **busca automática de sorriso + olhar** com o FaceMesh do mediapipe
  (`pip install mediapipe==0.10.14`, `refine_landmarks` = íris): boca larga e cantos subindo, nariz no meio das bochechas
  (yaw), íris no meio do olho; 6 quadros/s nos dois vídeos, 8 melhores com ≥2 s entre si numa folha E1–E8 / J1–J8
  (`out/capa_opcoes_{erik,jessica}.jpg`) para ela escolher. Na capa: A = jess 36,8 s (J4) + erik 110,2 s (E2); B = jess
  50,7 s (J6) + erik 113,0 s (E3); enquadramento pela posição do nariz (`NARIZ`). **Para foto de pessoa em capa: sempre
  sorrindo e olhando para a câmera.** **3ª:** ela pediu uma opção SÓ ESCRITA e centralizada "pra ler no feed" → C: fundo
  rosa × azul na diagonal com raios suaves e "?" claros, "ELE × ELA", "QUANTO A GENTE SE CONHECE?" enorme (168 px) no
  centro e "ACERTAMOS SÓ 1 DE 6?!"; conferido recortando 3:4 (y 240–1680) e reduzindo para miniatura. Depois ela pediu o
  fundo nas CORES DO LOGO: laranja #F48825 × azul-petróleo #1C7C96 (o selo ELE × ELA virou petróleo: amarelo no laranja não contrasta).
- **Capa do "Esse ou aquele? versão Jéssica" (`gravados-reels/capa_esse_aquele.py`, 23/out):** fundo nas cores do logo
  (laranja × petróleo na diagonal, igual à capa C do casal), "ESSE OU AQUELE?" no alto, a foto dela num cartão (quadro
  da busca de sorriso + olhar; folha J1–J8 em `out/capa_ea_opcoes.jpg`; ela escolheu a **J8 = 55,17 s**),
  fotos do site de Luxor e Wonderland's War nos cantos (1ª rodada, sem entregar o campeão) e "VERSÃO JÉSSICA".
  Depois ela pediu OUTRO FUNDO (mesmas cores): "todas as capas estão com o mesmo fundo" (a diagonal com raios) → 3 opções
  `capa_esse_aquele_{1_xadrez,2_bolinhas,3_trilha}.png`. **Regra: variar o fundo entre capas também, não só entre carrosséis.**
- **Taco Gato Cabra Queijo Pizza (`taco-reels/`, 26/out, começando):** ele pediu "como se joga, tipo animação"; depois mudou
  para **DESENHO DE LÁPIS DE COR** (referência: post do @comeceevoluir, elefante × gato rabiscados em papel creme, contorno
  preto tremido em várias passadas, cor em hachura com o papel aparecendo, nome escrito à mão com setinha). Edição de
  vocês = **PaperGames** (Pocket R$ 15; site: 2–8 jogadores; PaperGames: 10 min, 6+). Cartas OFICIAIS planas no site da
  PaperGames (`wp-content/uploads/2022/07/cartas-frente-NN.png`, 544x741): 11 Gorila, 15 Taco, 16 Gato, 25 Narval, 28 Cabra,
  39 Queijo, 49 Marmota, 56 Pizza + `cartas-verso.png` → `assets/cartas/`. A caixa DELES **NÃO tem a Capivara** (ele corrigiu em 26/out): só Gorila, Narval e Marmota; a cena da
  capivara saiu (os arquivos `capivara*.png` ficaram em assets, sem uso). O texto impresso das cartas é RECORTADO (transparente) e fica a 9–21% / 79–91% da altura.
  Regras (PaperGames + Wikipédia; o folheto oficial está no OneDrive e o proxy bloqueia): vira a carta no monte do meio e
  fala a próxima palavra (taco, gato, cabra, queijo, pizza...); carta = palavra → todos batem, o ÚLTIMO leva a pilha;
  Gorila = bate no peito, Narval = mãos juntas em chifre na cabeça, Marmota = bate as duas mãos na mesa, depois bate na
  pilha; errar o gesto / bater sem precisar / hesitar = leva a pilha; vence quem, sem cartas, bate PRIMEIRO numa combinação.
  `lapis.py`: `lapis()` (contorno = traços pretos lum<100 em 3 passadas tremidas; cor = base clara + hachuras com a cor da
  arte saturada), `carta()` (sem o texto impresso, nome à mão em Kalam), `desenho()` (qualquer arte + contorno de fora).
  Mãos = **OpenMoji** com tom de pele (`assets/openmoji/*-pele.png`, SVG renderizado com cairosvg; têm contorno preto);
  o emoji Noto virou um borrão. Fontes de mão: Kalam, Patrick Hand, Gochi Hand (`assets/fonts/`). Teste: `teste.py`.
  **Vídeo: `taco-reels/taco.py`** (24 fps, desenho "tremendo" a 12/s: 3 sementes de cada sprite em cache; ~65 s, 9 cenas do
  roteiro aprovado: palavras se escrevendo + cartas, baralho distribuído em 4 montes (verso oficial), cartas virando no ar
  até o monte com balão da palavra e a ordem das palavras embaixo, GATO = carta → 4 mãos batendo com "PÁ!" e a pilha indo
  para o último, gorila/narval/marmota grandes com o gesto (punhos, mãos em chifre, mãos na mesa), erros riscados com X vermelho, "0 cartas" bate primeiro = GANHOU, "Comenta aqui: qual palavra você sempre
  erra?", tela final com a caixa oficial em lápis). Bichos grandes = arte da carta sem o fundo (`spr_arte`, flood fill da
  cor da borda, corte de 5% nas laterais para tirar o fio da carta). Imagens com fundo branco/transparente passam por
  `sem_fundo` (senão o contorno vira um retângulo). Ilustração chapada SEM contorno preto (gesto da capivara): `fino=True`
  (área escura grande = cor) + `bordas=True` (divisas de cor viram traço) + `traco=0.55` (riscos curtos), senão o gesto
  some. Tudo acima de y ≈ 1590 (legenda). **Letras (pedido dele: "feito à mão, mas que dê pra ler"):** `letra()` usa Patrick
  Hand com traço engrossado (stroke), cada letra com giro/tamanho/altura levemente diferentes, grão de lápis, 2ª passada
  POR BAIXO (por cima ela clareava tudo para cinza) e um "apagado" de papel em volta. 8 falas, 62 s.
  **Narração recebida (27/out):** 8 .webm NOMEADOS e na ordem certa (`narracao/raw/`). Ele mudou bastante as falas (TEXTO em
  `narracao.py` = o que ele falou; ex.: "é um party game", "você acha que você seria rápido o suficiente?" → a tela do
  "comenta" mudou para isso; narval "mãos em cima da cabeça" → "mãos na cabeça!"). Whisper `small` errou "Nossa vez",
  "exitou", "parigame": conferi com o `medium`. `narracao.py` tem MARCOS: a cena dos especiais (agora com 2,4 s de
  introdução "CARTAS ESPECIAIS!" + 3 blocos de 3,4 s) e o "comenta" são cortados em pedaços para entrar na palavra dita.
  O tremido do desenho usa o tempo FINAL (`_TN`), senão a cena esticada treme mais devagar. Saída: `taco_{legendado,
  sem_legenda}.mp4` (−15,5 LUFS, pico −2) e `_chat.mp4` (2 passadas a 2900k). `python3 taco.py --previa` = prévia sem voz. **2ª rodada:** tirou "5 dias de jogo" da tela final (pedido dele) e a
  RESPIRAÇÃO antes da 1ª palavra: `tratar_narracao.corta_respiro` (corta até o salto > −20 dB) + `corta_resto_respiro`
  (chiado SEM tom + silêncio de 30 ms + voz com tom → corta no silêncio; S/T no começo da palavra emendam na vogal, não
  cortam). Conferir o começo de cada frase_NN pela periodicidade (respiro = aperiódico). 64,6 s.
  **3ª rodada (27/out):** ele não gostou do áudio das falas 5 a 8 e vai REGRAVAR. Gravador só dessas falas (salva como
  `taco_narracao_05..08`): `https://raw.githack.com/erik-magalhaes/GitJoy/e7d66f33ae7cada130c0203b70bdb8d9fbb69081/taco-reels/gravador/Gravar_narracao_Taco_5a8.html`.
  **Regravação recebida** (arquivos `taco_narracao_0N_1.webm`; os antigos em `narracao/raw/v1/`). Ele pediu de novo:
  "corta as respirações nos inícios". A fala 6 tinha respiro + 0,35 s de silêncio antes de "Se": a regra do resto de
  respiro agora procura TOM em até 0,25 s depois do silêncio (o S chia antes da vogal). Whisper `small` ouviu "nerval":
  MARCOS aceita alternativas. 64,5 s. Gravador (arquivos `taco_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/7259c30f06370b1abad127624af5c10672c58050/taco-reels/gravador/Gravar_narracao_Taco.html`.
- **Linha Micro da PaperGames (`gravados-reels/micro.py`, 27/out):** 3 stories dele no Drive de brutos (`brutos/out27/`,
  fora do git), um por caixinha: 1·2·3 = O Que O Quê (o "QQ" dele), Duo Regna, Qui-Quitanda; 4·5·6 = ProcuRatos, Glifos,
  Glitches; 7·8·9 = Lemur, Córdoba, Lux Nova (Reiner Knizia, 10 min cada; fichas da PaperGames em `JOGOS`). No site são 3
  itens Pocket R$ 15 ("Linha micro 1, 2 e 3 (Papergames)"…; o 2º está escrito **"3, 4 e 6"** no site — avisei).
  **Câmera da frente = imagem ESPELHADA** (texto das caixas ao contrário): `hflip` na GRADE. Um Reels só com os 3: saíram
  "no próximo Stories / vou colocar o link", "Opa! Lado errado", "faz tenkano joguem, galera. Foi mal" e "de fazer... de
  ferrar". Fala a 1,1x, cortes pela energia (base do `taketime.py`), legenda palavra a palavra com `CORRIGE` (Whisper:
  "Kiki Tanda" = Qui-Quitanda, "Procuratus", "Glyphos"). Caixas 3D OFICIAIS da PaperGames (`papergames.com.br/<jogo>/`,
  `*_3D_frente.png`, recortadas do branco + sombra em `assets/micro/recorte/`): fileira da caixinha com os 3 acendendo no
  nome, caixa grande com a etiqueta do que ele disse, selos. As fotos do site das caixinhas só existem em 256 px.
  "Qual caixinha você levaria?" e tela final com as 3 caixinhas em leque. ~83 s.
- **3 carrosséis novos (28/out, ele escolheu da lista de ideias; 1080x1350, identidade da Jéssica, conceito próprio
  cada um, jogos que AINDA NÃO apareceram em carrossel, fichas do `acervo_site.json`, caixas de `hobby-reels/assets/acervo/`):**
  `feed-sua-vez/combos.py` = CARDÁPIO DE LANCHONETE (listras laranja × creme, letreiro marrom com lampadinhas, bandeja
  com 3 caixas, estrela de preço = soma dos aluguéis "os 3 por 7 dias", comanda): Casal (Allumbra, 1·2·3 Lucha!, Unmatched
  RH × Bigfoot = R$ 60), Família (Throw Throw Burrito, Tesouro do Dragão, Break the Cube = R$ 90), Galera (Blablabel, Ref!,
  Telma = R$ 60), Estratégia (Tikal, Dwar7s Fall, World Wonders = R$ 105); 7 telas. `feed-sua-vez/mitos.py` = MURAL DE
  CORTIÇA (post-it com tachinha + carimbo vermelho "MITO!" + ficha pautada "A VERDADE" com a caixa): coisa de criança →
  Detective; difícil → Coup; demora → BraveRats; muita gente → Cartógrafos (1 a 100); briga → The Goonies (cooperativo);
  caro → Bohnanza (R$ 15); 8 telas. `feed-sua-vez/amigo_secreto.py` (ele trocou Natal por AMIGO SECRETO) = PAPEL DE
  PRESENTE (petróleo com bolinhas e estrelinhas DESENHADAS — a Figtree não tem "✦" —, fita laranja com laço, papelzinho
  do sorteio "você tirou:", etiqueta kraft "TESTE ANTES:"): não gosta de jogo → Dobro, competitivo → High Society, casal →
  Sea Salt & Paper, criança → Uga Buga, estrategista → Istanbul: Jogo de Dados; final "pra festa: 3 jogos = 7 dias" +
  "Marca aqui quem você quer tirar!"; 8 telas. Zips em `out/carrossel_*.zip`. Pegadinha: fundo com `lru_cache` precisa
  devolver CÓPIA (senão as telas se desenham umas por cima das outras).
- **Carrossel de Halloween (`feed-sua-vez/halloween_carrossel.py`, 28/out, pedido da Jéssica):** "ESCOLHA SEU MEDO",
  conceito A PRATELEIRA DE TERROR DA LOCADORA (fitas VHS: estojo preto, faixa do gênero, caixa oficial na capa, etiqueta
  "LOCADORA SUA VEZ" com ficha e preço, adesivo "SEJA GENTIL: DEVOLVA EM 5 DIAS" (7 no Deluxe), letreiro neon vermelho,
  lombadas desfocadas). Assassino → Final Girl, zumbis → Tiny Epic Zombies (o Zombicide Rue Morgue só tem imagem de 276 px),
  vampiros → Drácula vs Van Helsing, fantasmas → Paranormal Detectives, monstros → O Vale dos Monstros II, perder a cabeça →
  Por favor, não corte minha cabeça!, "nada? então é família" → Scooby-Doo; final "Qual é o seu medo? Comenta aqui!". 9 telas.
  Ele disse "tem dois vídeos" = os 2 vídeos de Halloween que já existem (roxo e pôster); não chegou vídeo novo no Drive.
- **Carrossel "Jogos e dinâmicas na sua empresa" (`feed-sua-vez/empresas.py`, 28/out, ideia dele):** levar a monitoria de
  eventos para DENTRO das empresas, foco em comunicação/confiança/planejamento/resolução de problemas (NÃO quebra-gelo).
  Conceito CONVITE DE REUNIÃO DA AGENDA (grade de agenda com reuniões chatas desbotadas; cada tela um convite com duração,
  pessoas, "Local: sala de reunião (a gente leva o jogo)", PAUTA e "Vai participar? Sim/Talvez/Não"): Código Secreto:
  Imagens, The Mind, Take Time, Unlock! (recorte novo `hobby-reels/assets/acervo/unlock_timeless_adventures.png`, sobra
  laranja tirada) e Passaporte Mundo; ele TIROU o Sheriff of Nottingham. Final com WhatsApp (11) 97793-3910 e ABC Paulista.
  7 telas. **Trabalho dele (ele é analista de MELHORIA CONTÍNUA):** quer uma dinâmica de A3/PDCA com o time de 4 pessoas
  na sexta. Propus A "Kaizen do café" (Coffee Rush em 2 duplas no modo 2 jogadores; abas 1→4 = lead time, penalidade =
  cliente perdido, 3 xícaras = WIP; rodada 1 com nº FIXO de turnos → A3 → rodada 2 → comparar/padronizar) e B "Gemba no
  mapa" (MicroMacro: definir o problema, colunas FATOS × SUPOSIÇÕES, causa, conferir nas cartas). Ele gostou dos dois;
  ofereci o material (A3 adaptado, ficha de medição, regras em 1 página, roteiro do facilitador).
  **Kit do Coffee Rush FEITO (28/out):** `dinamica-kaizen/` (`kit.html` A4 + `a3.html` A4 paisagem → `python3 gerar_pdf.py`
  → `out/kaizen_do_cafe.pdf`, 5 págs: visão geral/agenda 90 min, roteiro do facilitador, regras em 1 página + jogo × processo,
  ficha de medição 12 turnos, A3 PDCA com 5 porquês/Ishikawa). Detalhes de regra que não confirmei ficaram como "veja o manual".
  **29/out:** a pág. 3 tinha 2 erros (corrigidos): o tabuleiro de ingredientes é uma GRADE 4x4, anda 1–3 casas SEM diagonal e
  pega o ingrediente de CADA casa em que entra (não só onde para); com 2 jogadores, no fim do turno, depois de descer, entra
  1 pedido novo na SUA aba 1. Regras conferidas no rulespal (manual) + Board Game Arena.
  **Vídeo explicativo DA DINÂMICA** (ele pediu: "não é explicar o jogo, é o contexto todo da dinâmica"; depois: "não quero vídeo
  explicando a REGRA" → saíram as 6 cenas de regra, 83 s): `coffee-reels/dinamica.py`
  (sem as regras, vertical, sem narração, visual do kit: Lilita/Figtree, marrom/creme/laranja/petróleo): ideia (joga → mede → A3 →
  joga de novo → compara = PDCA), quem joga (2 duplas = 2 jogadores), jogo × processo ("por que o Coffee Rush"), agenda 90 min, rodada 1 + ficha, A3 com 5 porquês de EXEMPLO, regra de ouro
  (muda o método, não a regra), rodada 2, comparar (barras de EXEMPLO) e padronizar, ponte com o trabalho. Peças OFICIAIS da
  Galápagos (API `ccstore/v1/products/CFR001`: caixa, componentes, foto dos ingredientes em fundo verde-limão, baristas):
  `recortes.py` (fundo/sombra = "R≈G−6, claro, azul baixo" ligado à borda + descascar sombra escura + inpaint da franja;
  peças de vidro com casco convexo e meio transparentes). Barista vermelho = o azul com o matiz girado. As fontes não têm
  ✓ ✗ ≈ → (Lilita): `marca()` desenha. Ele achou que também seria legal um vídeo explicativo SÓ DO JOGO (não feito ainda).
- **Vídeo dos EVENTOS (monitoria) (`eventos-reels/`, 30/out, pedido dele):** 3 visuais mandados (`conceitos.py` →
  out/conceitos.jpg): A "Monte seu evento" (tela de app com controles pessoas/idade/clima e os jogos mudando), B letreiro de
  feltro (letras brancas no feltro preto + fotos do site com fita), C trilha do ABC (as 7 cidades como casas de tabuleiro,
  o LOGO anda até o evento; nada de peão desenhado). Sem narração, só texto (como os outros sem gravar). **Ele escolheu a C** →
  `eventos-reels/trilha.py` (33 s, xadrez amarelo): gancho "VAI FAZER UM EVENTO? / A GENTE LEVA OS JOGOS!", trilha das 7 cidades
  com o logo pulando de Mauá até "SEU EVENTO" (confete, "CHEGAMOS!"), tipos de evento em cartas virando, "JOGOS PRA TODO
  MUNDO" (crianças: Uga Buga, Go Cuckoo, Happy Salmon; adultos: Dixit, Telma, Ref!; fotos do site), "E A GENTE FICA O EVENTO
  TODO" (logo andando do começo ao fim), CTA com WhatsApp e Direct + "Comenta aqui: qual evento seu precisava de jogos?".
  `base.OUT` trocado para sair em eventos-reels/out (`eventos_{com_trilha,para_musica}_final.mp4`).
  **Região dos eventos (30/out, ele corrigiu): TODO o ABC Paulista E São Paulo capital** (no CTA do vídeo: 2 pílulas
  "TODO O ABC PAULISTA" / "E SÃO PAULO CAPITAL"). Vale para as próximas peças de eventos.
  Lembrar: ainda NÃO fizeram evento (sem "já atendemos", sem fotos de evento); WhatsApp (11) 97793-3910.
- **Carrossel "SEU MÊS, SEU JOGO" (`feed-sua-vez/seu_mes.py`, 31/out, trend "Seu mês, seu bichinho" do @hippieartesanatos
  que ele mandou):** 1080x1350, papel pastel por mês, letra de mão (Patrick Hand engrossada, letra a letra tremida), caixa
  recortada do site no meio, frase do "personagem" do jogo no clima do mês + "jogo: X", logo pequeno no canto. Capa com as
  12 caixas em volta de "SEU MÊS, SEU JOGO (qual é o seu?)" e tela final "qual é o seu mês? comenta e marca". Meses: jan MLEM,
  fev Unicorn Fever, mar Everdell Duo, abr Sheriff of Nottingham, mai Critter Kitchen, jun La Granja, jul Next Station
  London, ago Boss Monster, set Wingspan, out DCeased, nov Bad Company, dez Flamecraft (sem repetir os do vídeo dos signos).
  Prévia aprovada; as 14 telas foram mandadas SOLTAS (ele pediu "sem zip").
  **Depois ele disse: "queria com ARTES ENGRAÇADAS como o sapinho CLT"** (ilustração doodle original). Testei recortar
  personagens da arte oficial (fotos Galápagos MLE001/SON101/FMC001 em `assets/mes_orig/`, fora do git; rembg isnet):
  falhou (dragão sumiu, gato pela metade, xerife com as cartas) e não teria o estilo doodle. Não tenho gerador de imagem:
  propus que ELES gerem as 12 artes num app de IA (ChatGPT/Gemini) com os prompts que mandei e eu monto as telas
  (letra de mão, mês, frase, caixa pequena no canto, logo), ou manter a versão com as caixas. **Ele fez no Gemini** (folha
  4x3 com os 12 bichinhos, `feed-sua-vez/assets/seu_mes/gemini_12.jpg`) → `bicho(k)` recorta cada célula (creme ligado à
  borda vira transparente; pedacinhos da célula vizinha que encostam na borda e têm < 4% da área saem). Tela do mês:
  bichinho grande no meio, frase embaixo, "jogo: X" e a caixa PEQUENA no canto de baixo à direita; capa com os 12 bichinhos
  em volta do título. 14 telas entregues soltas. **Rodada seguinte:** acharam o jogo "muito pequenininho" → 3 opções em `seu_mes.py --opcoes` (out/seu_mes_opcoes.jpg; `ESTILO` A fundo = caixa desfocada, B bichinho à esquerda + caixa grande girada com etiqueta kraft do nome, C polaroide com fita). Recomendei a B, mas **ele escolheu a A** (1/nov) e mandou uma folha NOVA do Gemini (mesma ordem; a antiga ficou `gemini_12_v1.jpg`). Na A a frase sobe (y 950) e a caixa nítida fica no canto de baixo à direita sem encostar nela; o creme do fundo agora é a mediana da borda de cada célula (muda entre folhas), e tiras finas de bichinhos vizinhos na borda da célula saem. 14 telas mandadas soltas. **Recorte refeito** (ele: gato, xerife e pernas da galinha com fundo branco): o rembg isnet (`_rembg`, máscaras em `assets/seu_mes/rembg_NN.png`) serve de JUIZ, não de recorte (ele deixa branco meio transparente): sombra de chão cinza ligada à borda sai se o rembg concordar, buracos de fundo presos no desenho (< 1,5% da célula) saem se o rembg disser fundo, e a franja clara do contorno fica meio transparente. **Mas** tirar buraco creme preso no desenho apagava a barriga do gato (o branco dos bichinhos é creme como o fundo): só saem buracos no PÉ da figura (centro abaixo de 80% da célula, rembg < 0,1). Ele também pediu para voltar ao **fundo de cor lisa** do 1º carrossel (`FUNDO_JOGO = False`); a caixa nítida segue no canto. Conferir recorte sempre num fundo verde forte, não no fundo final. **Versão FINAL (1/nov):** eles acharam os recortes da 2ª folha ruins e pediram para VOLTAR à 1ª folha (`gemini_12_v1.jpg`) com o 1º recorte e o fundo liso; só a caixa do jogo cresceu (175 → 255 px, canto de baixo à direita), frase em y 968 e "jogo: X" entre o logo e a caixa, sem encostar no texto. O código da 2ª folha (rembg juiz) ficou no histórico (commits e114a27/a7e81e0). **Ambiente novo (31/out):** `python3` aponta para
  o 3.11 sem pacotes; usar `/usr/bin/python3` (3.13, com PIL/numpy; instalei opencv-python-headless e imageio-ffmpeg).
  A cópia local veio ATRASADA em relação ao GitHub: sempre `git fetch` + reset/rebase para o origin antes de trabalhar.
- **Final Girl "O FILME" (`finalgirl-reels/filme.py`, 31/out = Halloween, pedido dele):** "um filminho com as artes do
  jogo" (Hans no acampamento, os jovens, a final girl fugindo/lutando, os outros assassinos da 1ª temporada) e **voz de IA
  liberada por ele** ("pode ser direto da IA"). Reaproveita o visual de `trailer.py` (importa como `T`): gancho HALLOWEEN /
  FINAL GIRL no Hans grande, mapa oficial do Camp Happy Trails escurecendo ("...até a primeira noite"), HANS o açougueiro
  com os retratos de Laurie e Reiko sumindo, a capa oficial do Happy Trails (final girl + Hans nas árvores) e as
  a outra final girl da capa alternativa do Happy Trails (Reiko, `FG-FF1-2`) encarando o Hans no "E REVIDA!" (**ELES NÃO
  TÊM MINIATURAS: o jogo deles vem só com meeples. Nunca usar foto de miniatura do Final Girl, só a ARTE do jogo**), os outros 4 assassinos com o título BR do filme,
  "você joga sozinho" (salve as vítimas / ache uma arma / enfrente o assassino), as 5 caixas BR, comenta e CTA com **7 dias**
  (Final Girl é Deluxe). **Aluguel do Final Girl (ele explicou 31/out): as 5 caixas NÃO vão juntas; a pessoa escolhe o
  jogo BASE + o filme (expansão) que quiser, e cada expansão tem o seu preço** → CTA "JOGO BASE + O FILME QUE VOCÊ
  ESCOLHER" e "cada filme é uma expansão alugada à parte" (saiu o "7 dias", que valia só para o base Deluxe); última fala
  "Aluga o jogo base e escolhe o seu filme". 70,0 s (LEAD/TAIL 0,4/0,55). Voz edge-tts Antonio −8% / −9 Hz + eco leve (`--voz` → `voz_ia/`, fora do git); cada cena = fala
  + 1,15 s (mín. por cena) → 69,4 s. Legendas por pedaços da frase, tempo proporcional às letras.
- **Sorteio do HITSTER + bônus (`promo/sorteio_hitster.py`, 31/out, ideia dele):** ele queria sorteio só para quem aluga;
  avisei que sorteio condicionado a compra precisa de autorização (Lei 5.768/71, Secretaria de Prêmios e Apostas). Ele
  escolheu: **sorteio ABERTO** (siga @suavez_bg, curta, marque 2 amigos) **até 15/11, resultado 16/11** + **bônus garantido
  separado: quem alugar até 15/11 ganha +2 dias de jogo**. Visual "festa do Hitster" (preto com luzes rosa/ciano/amarelo
  desfocadas, disco de vinil, equalizador no pé), identidade da Jéssica, caixa oficial Galápagos. Saída `promo/out/sorteio/`:
  post_1_sorteio + post_2_bonus (carrossel 1080x1350) e story_sorteio + story_bonus (1080x1920). Texto obrigatório:
  "não é patrocinada nem administrada pelo Instagram" (ele pediu para TIRAR da imagem o "não precisa alugar nem comprar
  nada": isso fica só na legenda). Prêmio: retirada em Mauá ou envio (sem citar custo de frete).
  **Lembrete em vídeo para os Stories** (`promo/sorteio_story.py`, 9/nov, "bem rapidinho, só pra lembrar"): 9 s, mesmo
  visual com as luzes pulsando na batida e o equalizador mexendo, LEMBRETE! / SORTEIO DO HITSTER!, disco girando atrás
  da caixa, 3 passos, "toca aqui e participa:" + seta e espaço livre (y≈1450–1610) para o adesivo do post, datas, bônus
  de +2 dias e o aviso do Instagram → `promo/out/sorteio/lembrete_{com_som,para_musica}_final.mp4`.
- **Tikal (`tikal-reels/`, 10/nov, pedido dele: "vídeo explicando, tipo animação"):** edição deles = **Super Meeple** (no Brasil
  pela **Conclave**; site: Estratégico R$ 45, 2–4 jogadores, 90 min). Material OFICIAL da Super Meeple
  (`supermeeple.com/en/tikal`, wp-content): manual francês `ReglesTikalBD.pdf`, renders `TIKALmeeple/tresors/temples` e a
  capa 3497 px → `assets/orig/` (fora do git). `recortes.py` → `assets/pecas/`: hexágonos do manual a 400 dpi com máscara de
  hexágono (lado plano em cima) + Real-ESRGAN (a seta branca da ruína tirada com inpaint), meeple branco sozinho (tingido por
  cor em `pecas.meeple`) e as 8 fichas de tesouro (grade 4x2 medida com HoughCircles). **Regras conferidas** (manual +
  rulespal): tira o hexágono do monte e encaixa; 10 PA: explorador no acampamento 1, andar 1 por LAJE do caminho, andar de
  templo 2 (máx. 2 por templo/turno, 1 explorador por andar), cavar tesouro 3, trocar tesouro 3 (o outro não recusa),
  acampamento 5, guardião 5 (precisa ter a maioria; templo fica seu até o fim; máx. 2); chefe vale 3 na maioria, empate
  ninguém pontua; tesouros 1/3/6 (um, par, trinca); 3 vulcões (B, D, F) = contagem, cada um gasta 10 PA antes de contar;
  contagem final depois do último hexágono. `conceitos.py` → out/conceitos.jpg: A mapa vivo, B trailer na selva, C caderno
  do arqueólogo. Ele respondeu só "faz o vídeo" → fui de **B** (esconde a resolução baixa dos hexágonos).
  **`tikal.py`** (65 s, 9 cenas, prévia sem voz `out/tikal_previa_final.mp4`): capa oficial em tela cheia (recorte abaixo do
  logo e acima dos autores, Ken Burns lento, raios de luz), tabuleiro de hexágonos em PERSPECTIVA (`camera()` = homografia
  foco/zoom/giro + inclinação fixa; peças em pé com `de_pe`), letreiro Cinzel dourado com halo escuro, 10 tabuletas de PA
  apagando, placas de custo, andares de templo caindo com o selo do valor, tesouros 1/par/trinca, placar da maioria (chefe =
  3), guardião subindo no templo, troca de tesouro, vulcão com tremor e brilho laranja, comenta e tela final com a caixa do
  site ampliada (Real-ESRGAN). Trilha de selva sintetizada (`trilha()`: tambores, chocalho, marimba pentatônica). Gravador
  (arquivos `tikal_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/853c8c22acbc846354f5acbea2eb900ced3c7819/tikal-reels/gravador/Gravar_narracao_Tikal.html`.
  Ao receber: `narracao/raw/` → tmp_NN.wav (cadeia de voz, 44,1 kHz) → tratar (taco-reels/tratar_narracao.py) → `narracao.py`
  (gerar `narracao/timeline.json` com cena/ini/dur/palavras) → `tikal.py` (lê a timeline sozinho).
  **Opção C também (pedido dele, 10/nov): `caderno.py`** = CADERNO DO ARQUEÓLOGO com o MESMO roteiro e a MESMA linha do
  tempo (importa `tikal` como T: TL, TEXTO, legenda): cada fala é uma página pautada (margem vermelha, furos de espiral,
  nº da página) que VIRA saindo pela esquerda sobre a mesa de madeira; fotos instantâneas com fita (hexágonos, capa, caixa),
  adesivos com borda branca (meeples tingidos, tesouros, logo do Tikal), escrita à mão que se revela (`escreve`, Patrick
  Hand/Kalam, caneta azul), caneta vermelha (`circulo`, `seta`, `sublinha`), post-its com o custo em PA, 10 quadradinhos
  riscados com X, risquinhos de contagem e carimbos (GUARDADO, CONTAGEM!, COMENTA AQUI!). Som: violão dedilhado + chocalho,
  caneta riscando, página virando. Prévia `out/caderno_previa_final.mp4`. A mesma narração (`tikal_narracao_NN`) serve pros dois.
  **2ª rodada do caderno ("mais realista as escritas e a folha, NADA DE ANIMAÇÃO"):** `papel.py` = folha fotografada
  (fibras em várias escalas, luz do alto à esquerda, curvatura escura perto da espiral de ARAME, pauta impressa fina e
  irregular) + tinta de esferográfica (**Caveat** do google/fonts em `assets/fonts/`, letra a letra com giro/altura/tamanho
  variando, linha de base ondulando, falhas e pressão, aplicada em MULTIPLICAR sobre o papel). Nada pula, cresce, voa ou
  vira: as peças só APARECEM no lugar (foto a foto), a página troca com corte seco, carimbos são impressos em multiplicar;
  só a caneta escreve/circula no ritmo da mão. Texto sentado na pauta (`linha(n)`), legenda das fotos escrita na borda
  branca. O "→" não existe na Caveat (usar "...").
  **3ª: "DIÁRIO DA EXPEDIÇÃO" (`diario.py`, pedido dele: "só as imagens e poucas anotações, eu narro como se
  estivesse documentando")**: mesmo papel/tinta, fotos GRANDES, anotações de 1–3 palavras (custos, = 1/3/6, chefe = 3,
  carimbos). FALAS NOVAS em 1ª pessoa (`TEXTO` no diario.py; troca `T.TEXTO`/`T.TL` do tikal.py em tempo de import), cada
  página = fala estimada a 15,5 letras/s + 0,8 s (69 s sem voz). Gravador (arquivos `tikaldiario_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/ee1cd3d29d928afd15f7e6c6c9cfb4c15a2354be/tikal-reels/gravador/Gravar_narracao_TikalDiario.html`.
  Ao receber: tratar → `narracao_diario/timeline.json` (cena/ini/dur/palavras) → `diario.py` lê sozinho.
  **NARRAÇÃO RECEBIDA (10/nov, 9 .webm nomeados):** cadeia de voz no ffmpeg → `tmp_NN.wav` → `tratar_diario.py` (cópia do
  tratar_tarde: respiro/silêncio/pausas ≤0,3 s + Whisper small) → `narracao_diario.py` (LEAD 0,25 / TAIL 0,35, tela final
  3,2 s depois da fala; `CORRIGE`: ticar→Tikal, tempos→templos, ruída→ruína, "alugue -te calma a sua vez"→"aluga o Tikal
  na Sua Vez"; o "comenta" vira tela final no "aluga") → `diario.py` (mistura própria `mixa_voz`: trilha abaixa sob a voz)
  → `out/diario_{legendado,sem_legenda}_final.mp4`, 68,9 s. Ele mudou a fala 8 ("...vimos quem conseguiu fazer mais pontos").
  **2ª gravação (10/nov, "quero gravar de novo"; arquivos `_1.webm`, a 1ª ficou em `raw/v1/`):** ele improvisou mais ("Dia 2
  / Dia 3 do diário de expedição", "acho que tem até uns vulcões", "Ele não pode recusar, mesmo!") e a voz somou 73 s →
  `atempo=1.12` no tmp_NN.wav antes do tratamento, pausas ≤0,22 s, LEAD/TAIL 0,15/0,15, tela final 2,3 s → 69,8 s. O texto
  da legenda é o que ele FALOU, conferido com o Whisper **medium** (`TEXTOS` + `alinha()` no narracao_diario.py: tempos do
  small, repartidos pelas letras quando a contagem de palavras não bate). Títulos das páginas 4 e 6 viraram "Dia 2"/"Dia 3".
  **Imagens em HD (10/nov, ele: "o vulcão tá bem ruim; meeples com a cabeça cortada"):** os hexágonos do manual são
  pedaços raster de ~140 px (não tem como ficar HD). Fonte MELHOR: as peças DIGITAIS oficiais do Tikal no **Board Game
  Arena** (`x.boardgamearena.net/data/themereleases/current/games/tikal/260729-0805/img/` → TikalTerrains.png = 6x8
  hexágonos de 277 px, TikalTokens.png = tesouros e totens com alfa, TikalBoard.jpg 2000 px; versão do jogo no JSON da
  `gamepanel?game=tikal`) + fotos oficiais do jogo montado (`data/gamemedia/tikal/display/0..9.jpg`, ~1140 px, templos de
  resina e meeples) → `assets/orig/` (fora do git). `recortes.py hexagonos_bga tesouros_bga` (ESRGAN x4 → ~1100 px).
  Meeple novo = o BRANCO da foto display/8 (ESRGAN x4 + rembg isnet), cabeça inteira, tingido como antes.
  **Para outros jogos: o BGA tem as peças digitais oficiais (css do jogo lista os sprites).**
- `architects-reels/arq.py` (planta azul) e `mlem-reels/mlem.py`/`stopmo.py` são versões **rejeitadas**. Ficam só como referência.
- **Reels "TIRA PRINT: qual jogador você é?" (1/nov, ideia dele: tarô + bichinho engraçado):** loop curto como o
  `roleta-reels/taro.py` (troca a cada 2 quadros), uma carta grande com bichinho + tipo de jogador + jogo do acervo.
  Arte: ELES geram no Gemini (prompt mandado no chat): estilo ORGÂNICO tipo "sapinho CLT" (pintura texturizada, traço
  irregular, nada liso/vetorial), folha 4x3 com CADA quadro de fundo próprio de cor lisa até a borda e espaço branco
  entre eles → corte RETANGULAR, sem recortar o bicho (lição do Seu mês). Lista v2 (ele cobrou que o bicho tenha a ver com o jogo; na 1ª metade era só metáfora): o BICHO VEM DO JOGO e a
  piada vem da mecânica: bode (o BOM, o MAU e o BODE), castor (Beaver Creek), macaco (Monkey Palace), camelo que aposta no
  último segundo (Camel Up), rato que dispara na frente (First Rat), abelha rainha encurralada (Hive), tubarão que só quer
  ver o circo pegar fogo (Survive the Island), dinossauro que pega a peça que você queria (Draftosaurus), dragão que não
  divide (Tesouro do Dragão), gato que empurra todo mundo (boop.), peixe esquisito arrependido (Deep Regrets), camaleão
  com máscara que blefa (Mascarade). **Feito: `bichos-reels/bichos.py`** (arte deles em `assets/gemini_bichos.jpg`, quadros achados pela faixa branca; quadro INTEIRO na carta e as laterais na cor lisa do fundo): fundo petróleo pontilhado, "QUE JOGADOR VOCÊ É?" + "TIRA PRINT E DESCOBRE!", carta creme com contorno e sombra marrom (bichinho, "O QUE...", caixa + JOGO:), troca a cada 2 quadros, loop de 8 s (240 quadros), trilha "brincalhona" (marimba em loop). Caixas novas do site recortadas: o_bom_o_mau_e_o_bode, beaver_creek, first_rat (laranja tirado por matiz + casco convexo) em hobby-reels/assets/acervo/. Mandado.
- **Vídeos em LOOP que dão replay (1/nov):** mandei 6 ideias (qual caixa sumiu, pergunta no fim/resposta no começo,
  frase em loop "só mais uma partida", POV explicando as regras (gravado), organizando a caixa (gravado, "satisfatório"),
  jogo da memória). **Ele escolheu 1 e 6**, feitos em `loops-reels/` (`comum_loop.py` = entrega com/sem trilha a −15,5 LUFS,
  trilha "brincalhona" do bichos): `sumiu.py` (7 s: estante de madeira com 9 caixas do acervo — Echoes of Time, Treasure
  Island, Encantados, Savernake Forest, Cóatl, Metro, Dice Colony, Sideral, World Wonders —, "DECORA!" + barrinha 3,6 s, flash,
  some o METRO, "?" no lugar; no recomeço a caixa volta = resposta) e `memoria.py` (8 s: os 12 bichinhos do Gemini, "DECORA! 3-2-1",
  viram em onda para versos numerados, "ONDE ESTAVA O CAMELO? COMENTA O NÚMERO!" (resposta 4), desviram no fim). Mandados.
  Ainda não feitos: o 4 (POV das regras) e o 5 (organizando a caixa) dependem de gravação deles.
- **Sky Team "pilotar um avião em 1 minuto ou menos" (`gravados-reels/skyteam.py`, 1/nov):** 7 vídeos dele no Drive de brutos
  (VID_20261101_08xxxx → `brutos/nov01/<hhmmss>.mp4`, fora do git; gancho com a caixa na câmera da frente = ESPELHADO → hflip).
  Base = `taketime.py` (contra o relógio), cara de AVIAÇÃO: painel de aproximação no alto à esquerda (✈️ anda até a pista
  enquanto o cronômetro desce de 1:00; chega na pista no fim da explicação), selos das regras, carimbo "POUSOU EM 46 SEGUNDOS!"
  com palmas, "Você confiaria no seu par pra pousar esse avião? Comenta aqui!", tela final com a caixa (foto do site
  recortada, `assets/sky/sky_team.png`). Explicação a 1,1x; o gancho e o trecho da "buzina" vão INTEIROS (a pergunta "Ué,
  avião tem buzina?" é de outra voz, ~12 dB mais baixa: `REFORCO` +9 dB). Whisper (small e medium) ouve "flares": na
  legenda e no selo ficou **flaps** (avisei). No site: "Sky Team (em inglês)", Família R$ 30, 2 jogadores, 20 min (é a
  edição em inglês). 70 s. **2ª rodada:** ele ouviu o "1 minuto ou menos" cortado: o celular parou de gravar no começo do "s" de "menos" (chiado só a 2,97 s, último quadro) → emendado o "s" do "pessoas" dele (084743, 3,61–3,78 s, ganho daquele arquivo) e o gancho ganhou 0,25 s de quadro parado. **Bruto que termina colado na última palavra: medir o agudo do fim antes de montar.** **3ª:** "a parte dos flaps cortou tudo": o corte por energia (limiar piso+14 dB, herdado do Take Time) picotava fala baixa no meio da frase → limiar piso+8 (mín. −42 dB): só corta pausa de verdade. Conferir sempre que TODAS as palavras do Whisper caem dentro de algum pedaço. 74 s.
- **"TOP 10 ÀS CEGAS" da Jéssica (`gravados-reels/top10.py`, 1/nov):** 2 vídeos dela (20261101_151657 e _151838 no Drive de
  brutos → `brutos/nov01b/`, fora do git; o gdown lista só 50 arquivos por pasta: arquivos novos se acham pelo conector
  do Drive, `parentId = '1yGgK...' and createdTime > ...`). O Erik (fora da câmera) fala o jogo e ela escolhe a posição na
  hora. Top 10: 1 Trio, 2 Coffee Rush, 3 King of Tokyo Duel, 4 A Ilha do Tesouro (Treasure Island), 5 Mascarade, 6
  Cartógrafos, 7 Tikal ("Chicão" no Whisper), 8 The Resistance ("que já deu muita m*rda" → legenda censurada), 9 **Nem a
  Pato!** (Grok, NÃO está no site; caixa da loja da Grok), 10 Telestrations na Madruga (a foto do site é a After Dark).
  Pedido dele: imagem do jogo de um lado + a POSIÇÃO. Visual: escadinha 1–10 à esquerda; caixa grande à direita com o
  nome e "QUE POSIÇÃO?" quando ele fala; no número dela a caixa voa (arco por baixo, por cima passava no rosto) até a casa
  e o número acende; legenda ESCRITA à mão (`LEG`, o Whisper errou muito); fim: "O TOP 10 DA JÉSSICA" em 2 colunas,
  "E o seu nº 1, qual seria? Comenta aqui!" e tela final ("quase todos esses estão no nosso acervo"). Caixas em
  `assets/top10/`. ~54 s. **Versão ERIK** (`python3 top10.py --erik`; `PERFIS` no script, tempos do BRUTO): 1 vídeo dele (152424, 2:08) com a
  Jéssica perguntando. Saíram o começo (0–21 s), a recapitulação "já foi o 4, 9, 6..." (51–67 s) e a 1ª tentativa
  confusa do Paranormal (91–113 s; eles refazem). Top 10 dele: 1 Flip 7 (a do site é "A Vingança"; recorte refeito com o
  casco de TODOS os pedaços grandes, o maior sozinho cortava o topo creme), 2 MLEM, 3 Marvel United: Deadpool, 4 Ticket to
  Ride (o NORMAL; eu tinha posto o Legacy e ele corrigiu), 5 Coup, 6 Zombicide (Rue Morgue), 7 Metro, 8 Paranormal Detectives, 9 Taco Gato Cabra
  Queijo Pizza ("dói a mão"), 10 Draftosaurus. ~80 s. Legenda quebra em linhas de até 760 px (antes cortava na borda). **2ª rodada (Erik):** a escadinha à esquerda ficava em cima do rosto dele → no perfil dele `lado="dir"`: escadinha à DIREITA (236 px, colada na borda), caixa grande à esquerda e mais baixa, legenda deslocada para a esquerda e SEM o selo "QUE POSIÇÃO?" (batia no rosto ou na legenda). A da Jéssica continua como estava. Como todos os 10 do Erik estão no site, a tela final dele diz "TODOS ESSES ESTÃO NO NOSSO ACERVO" (`acervo` no perfil).
  **Capa do Reels do Erik** (`gravados-reels/capa_top10_erik.py`, 2/nov): fundo NOVO (azul-noite com holofote e confete), "SEM SABER O
  PRÓXIMO JOGO!", "TOP 10 ÀS CEGAS", "VERSÃO ERIK", caixas do 2º ao 10º numeradas em 3x3 e o Nº 1 ESCONDIDO ("QUAL FOI O Nº 1
  DELE?") para dar curiosidade; tudo dentro de y 285–1635. 2ª rodada: foto dele ao lado do título; ele pediu a da JOIA (124,6 s do 152424, cartão de cantos redondos;
  recorte até y 850 porque logo abaixo ele segura o Flip 7 = o Nº 1). 3ª: "olhando pro lado e só o título" → `--foto`:
  quadro em tela cheia (89,0 s rindo pro lado; 36,0 s pensativo; a ESCOLHIDA foi 13,5 s, `erik_lado3.jpg`, zoom 1,0 → `capa_top10_erik_foto3.png`). 4ª ("muito simples, seja criativo, cores da logo, logo no canto"): `--final` → balão de pensamento "E AGORA? ONDE EU PONHO?" com 3 caixas "?", selo "ELE NÃO SABIA O PRÓXIMO JOGO!", TOP 10 amarelo + ÀS CEGAS em faixa laranja, 10 casas "?" sobre petróleo listrado, logo grande no canto. 5ª: "as caixas do top 10 atrás, preenchendo o fundo" → `capa_top10_erik_caixas.png` (`colagem()`: as 10 caixas giradas e sobrepostas, escolha gulosa sem repetir caixa num raio de 820 px, começando pela área à vista; ele recortado com rembg `u2net_human_seg` → `erik_lado3_recorte.png`, contorno branco, some antes do Flip 7 da mão). 6ª: ele pediu para TIRAR o balão de pensamento (`com_balao=False`). 7ª (a usada): ele escolheu no editor do Instagram o quadro rindo de olho fechado com o Flip 7 na mão (21,15 s, `erik_rindo.jpg`) e pediu "só a logo e TOP 10 ÀS CEGAS, sem firula" → `--simples`: título amarelo em 3 linhas à esquerda, sobre a camiseta, ao lado da caixa + "TOP 10 ÀS CEGAS" sobre degradê azul-noite que esconde o Flip 7.
- **Capa do TOP 10 da JÉSSICA (`gravados-reels/capa_top10_jessica.py`, 6/nov):** igual à `--simples` do Erik (quadro em
  tela cheia, "TOP 10 / ÀS / CEGAS" amarelo à esquerda, logo no canto de cima à direita). Quadros mais nítidos (±0,4 s) do
  151838 → `assets/capa/jess_top10_b*.jpg`; 4 opções (b13.20, b14.70, b07.00, b16.00) em `out/capa_top10_jessica_opcoes.jpg`;
  no 151657 a carta fica em cima do título. **Escolhida: b13.20** (opção 1, "b014" da folha de quadros) → `out/capa_top10_jessica.png`; ele pediu também a com o b16.00 ("b017", opção 4) → `out/capa_top10_jessica_b017.png`.
- **Stories "SEMANA CURTA" (`feed-sua-vez/story_semana_curta.py`, 2/nov, feriado de Finados; pedido dele: levar gente pro
  site, "as pessoas ainda não têm alugado"):** conceito AGENDA (folha de agenda creme com espiral sobre mesa laranja
  listrada), 3 telas: 1 "SÉRIE OU JOGO? / Hoje à noite, você vai de quê?" + espaço livre (y 1000–1380) para a ENQUETE
  do Instagram (a 1ª, "quanto tempo sobra pra jogar depois do trabalho?", ele achou "ruimzinha"); 2 "SEMANA CURTA, JOGO RÁPIDO!": TER Bad Signs, QUA Flash 10, QUI Loser (Pocket, fichas do site),
  SEX "o jogão: você escolhe", faixa "3 JOGOS POCKET = R$ 45 e os 3 ficam 7 dias"; 3 "BÔNUS DA SEMANA" (+2 dias até 15/11,
  do sorteio do Hitster) + espaço do adesivo de link (y 1475–1610).
- **Noite de jogos em café (`proposta-cafe/`, 3/nov):** ele está desanimado (nenhum aluguel ainda, precisa de renda extra)
  e quer fechar com cafés. Sugeri R$ 20–25; ele quis 2 opções: **R$ 15 só os jogos (consumo 100% do café)** ou **R$ 30 com
  R$ 15 de consumação no café**. `proposta.html` → `gerar_pdf.py` (A4, 2 págs, identidade da Jéssica; Playwright com
  `executable_path="/opt/pw-browsers/chromium"`, o pip 1.56 procura outro build) → `out/proposta_noite_de_jogos.pdf`.
  Capacidade proposta: 6–8 mesas, 24–30 pessoas, 3 h; ele lembrou que pode ser À TARDE → título "TARDE OU NOITE DE JOGOS NO SEU CAFÉ" (tarde: fim de semana 14h–17h, famílias; noite: dia de semana 19h–22h), PDF `out/proposta_jogos_no_cafe.pdf`; a Sua Vez leva 20–30 jogos, monitoria, divulgação
  e inscrições. **Concorrência:** Bravo Jogos (Santo André, R. Cel. Alfredo Flaquer 411) cobra R$ 20 para jogar à vontade,
  ~500 jogos, com monitores (DGABC, mai/2026) → Mauá não tem espaço assim. Cafés achados (diretórios, CONFERIR): Mauá —
  Mocha 281 (R. Álvares Machado 281, Vila Bocaina, "aconchegante"), Waffle Station Coffee Shop (Av. Guilherme Polydoro 23,
  Jd. Zaíra), Coffee Break (Av. Pres. Castelo Branco 2669, abre 17h–0h), Café com Arte, Dumont Café; Ribeirão Pires —
  Ana Rosa Café (R. Afrânio Peixoto 20), Atelier do Café (R. Miguel Prisco 286), Senhor Café / Espaço Cafeteria (R. do
  Comércio 127), Café Bistrô (Centro Alto); Santo André — Mais1 Café (Vila Gilda e Vila Assunção), Café do Loft, Chaplin.
  Ele lembrou do **Democrata Café** (Mauá; cardapio.menu: "aconchegante, bem decorado", R$ 20–40). Ele vai abordar
  primeiro pelo DIRECT do Instagram. A busca na web NÃO acha @ de cafés pequenos (Instagram não indexa): não inventar @;
  mandei os termos de busca e a mensagem (curta, pessoal, pergunta se pode mandar a proposta; seguir/curtir antes).
  **Versão BAR** (ele: "e bar mais sossegado?"): `gerar_pdf.py` gera também `out/proposta_jogos_no_bar.pdf` (troca café → bar).
  Bares achados (CONFERIR): Ribeirão Pires — DB Tap House (@Dometilhasbeer, guia de turismo da cidade), Órbita Chopp
  Artesanal (qua–dom 14h–23h), Duck II Chopperia (R. Miguel Prisco 96, pode estar fechado); Santo André — M5 Cervejaria
  ("sem pressa"), Santuário da Cerveja, Fritz Cervejaria Artesanal, Sigilo Total Tap House, Cervejaria Madalena (bar de
  fábrica); Mauá — só choperias de diretório (Vicente Chopp, Cobra de Gelo, Casa do Chopp, Santa Petiscaria).
  **Becas Café** seguiu a @suavez_bg de volta (3/nov): foi o 1º café abordado pelo Direct (mensagem própria; não achei nada dele na web).
  Eles ACEITARAM receber a proposta → proposta virou **TARDE DE JOGOS, SÁBADO 13h–19h** (ele trabalha à tarde nos dias de
  semana), SEM prometer nº de pessoas nem 3 h (ele: "não tem como garantir"), roteiro 13h/13h15/14h30/16h/"a tarde toda
  entra quem chegar"/19h, "Locadora" (não "Locação"). `gerar_pdf.py` tem `LUGARES` → versão com o nome do lugar
  (`out/proposta_becas.pdf`: título "TARDE DE JOGOS NO BECAS CAFÉ" e "o Becas" no texto). Detalhe do Becas que ele viu:
  guarda-chuvinhos coloridos pendurados no teto. O Direct do Instagram NÃO aceita PDF: `gerar_pdf.py` também salva cada página em JPEG 1440 px (`out/<nome>_paginaN.jpg`).
  **Democrata Café (5/nov):** versão da proposta com o nome do lugar (`LUGARES["democrata"]` → `out/proposta_democrata.pdf` + JPEGs).
  **O Becas ACEITOU (3/nov)**; preocupação deles: espaço e não atrapalhar o movimento/ticket normal. Data em discussão
  (ideia dele: **20/11, feriado**, que não mexe com o sábado do café) → artes SEM data ("DATA EM BREVE"). Decisões dele:
  ingresso **R$ 30 com R$ 15 de consumação**, ~30 vagas (NÃO vai na arte: ele pediu para tirar), inscrição pelo **WhatsApp ou na hora no café**, cupom de **10% no
  1º aluguel** para quem participar (código sugerido `BECAS10`, eles precisam criar no site). `promo/tarde_becas.py` →
  `promo/out/becas/`: post 1080x1350, story 1080x1920, cupom 9x5 cm e `cupons_A4.pdf` (10 por folha, marcas de corte).
  Conceito: os GUARDA-CHUVINHOS coloridos do Becas pendurados no alto, creme quente, leque de caixas (Hitster, Dixit, Telma,
  Tapalavras, Say my Name, Uga Buga). 2ª rodada: ele AMOU os guarda-chuvas; tirou "Só 30 vagas" (3º item virou "Venha sozinho,
  em dupla ou com a galera") e a faixa virou "GARANTA SUA MESA PELO WHATSAPP / (11) 97793-3910 / Não reservou? Passa lá no
  dia: se tiver mesa livre, é só chegar e jogar!" (puxar pro WhatsApp sem desanimar quem quer ir no dia).
  Linktree sugerido (ele vai criar): reserva da tarde (wa.me com texto pronto), acervo, assinaturas, eventos, contato.
  **Reels do evento** (`becas-reels/tarde.py`, 3/nov): mesmo visual das artes, guarda-chuvinhas caindo e BALANÇANDO no
  alto o vídeo todo (pêndulo, `guarda_chuvas(img, t)`), 30 s sem narração: gancho "BORA JOGAR NUM CAFÉ?" / TARDE DE JOGOS
  / DATA EM BREVE → como funciona (3 passos) → os 6 jogos da arte → R$ 30 (card da arte) → "TRAZ QUEM VOCÊ QUISER" →
  CTA com WhatsApp + "Comenta aqui: qual jogo você quer aprender?". Importa `promo/tarde_becas.py` (TB). Quando a data
  fechar, trocar `TB.selo_data` nos dois scripts. Saída `becas-reels/out/becas_{com_trilha,para_musica}_final.mp4`.
  **3/nov, "os vídeos estão todos iguais, mesmos sons; seja imaginativo, use trechos que a gente já tem":** 3 conceitos
  NOVOS para o Becas em `becas-reels/conceitos.py` → out/conceitos.jpg: 1 PARA DE ROLAR (o vídeo finge ser o feed cinza,
  a tela trinca e estoura em cenas reais coloridas), 2 JOGO DAS XÍCARAS (3 xícaras embaralham, "onde está o dado? comenta
  1, 2 ou 3", a resposta abre o convite; replay), 3 6 HORAS EM 30 S (cenas reais deles em cortes no ritmo + relógio gigante
  13:00 → 19:00 com etiquetas). Som de cada um com cara própria (rolagem/estalo de vidro; xícaras de louça; relógio/cortes),
  NÃO as trilhas sintetizadas de sempre. Esperando ele escolher. Brutos locais: Sky Team (nov01) e top 10 (nov01b).
  **Ele pediu os TRÊS (3/nov) e "priorizar os JOGOS, as cenas de jogo na mesa":** baixei as cenas de mesa do Drive de
  brutos para `gravados-reels/brutos/mesa/` (fora do git): art_society, canvas, critter, passaporte, sushi, unlock (cenas do
  "indica" de 17/out), taketime/taketime2 (18/out), micro, lv (rosto da Jéssica). Base `becas-reels/kit.py` (CLIPES, cache
  de quadros em out/_cache, cor leve, `card_cta`, `entrega` → `<nome>_{com_som,para_musica}_final.mp4`) e SONS NOVOS em
  `becas-reels/sons.py` (rolagem, vidro, louça, sino, tique-taque, obturador, despertador; músicas pop 118 bpm, lounge de café,
  relógio que acelera). `para_de_rolar.py` (21,8 s: feed cinza → trinca → cacos → 13 cortes na batida com o nome do jogo →
  convite), `xicaras.py` (24,6 s: dado sob a xícara, 11 trocas, "COMENTA 1, 2 OU 3!", resposta 3, o dado cresce e vira
  montagem "NO BECAS, O JOGO É DE VERDADE!" → convite) e `seis_horas.py` (27,3 s: placar 13:00 → 19:00 + linha do tempo,
  10 cenas com etiqueta do horário, despertador "19H?! JÁ ACABOU?!" → convite).
  **Ele NÃO gostou dos 3** (para de rolar, xícaras, 6 horas; "não gostei de nenhum, talvez algo pra gente narrar") e pediu
  as 5 ideias narradas/gravadas, "faz todos": roteiros em `becas-reels/roteiros_narrados.md` e gravadores em
  `becas-reels/gravador/` (Documentario = becasdoc, Futebol = becasgol, Zap = becaszap). Esperando as gravações.
  **Esclarecido (3/nov):** 1, 2 e 3 são SÓ VOZ (eu faço o vídeo antes com as cenas que eles já têm; eles narram depois);
  4 (garçonete) e 5 (primeira vez) precisam de gravação no Becas. Prévias sem voz em `becas-reels/narrados.py <doc|gol|zap>`
  (tempo de cada fala estimado pelas letras; doc 13 letras/s, gol 15, zap 14,5; ao receber a narração, trocar pelos tempos
  reais): doc = faixas de cinema + legenda de documentário "JOGADOR DE TABULEIRO / Ludens tabulae · espécie rara" + cena do
  Becas com guarda-chuvinhas ("HABITAT TEMPORÁRIO") + cordas/piano (`sons.musica_doc`); gol = placar de TV MESA A x MESA B,
  AO VIVO, relógio 1ºT, GOOOOL com confete e REPLAY em câmera lenta, VAR "checando o lance" → "SEM VAR!", torcida e apito;
  zap = bolha de áudio tocando (onda, tempo) + "Erik · gravando áudio..." + "MARCA O AMIGO QUE NUNCA TOPA NADA!". A fala 3
  do zap foi trocada para Canvas/Unlock!/Critter Kitchen (eles não têm cena do Happy Salmon/Hitster).
- **ESTILOS NOVOS (3/nov, referências do Pinterest dele: colagem de letras recortadas "GAME NIGHT!", tabuleiro roxo + lima
  "noite de jogos", TVs retrô empilhadas com tela verde):** ele quer "fontes novas, cores novas, sair do basicão, até pros
  vídeos do dia a dia". Fontes baixadas do google/fonts para `comum/fontes/` (Anton, Abril Fatface, Archivo Black, DM Serif
  Display, Rubik Mono One, Shrikhand, Bebas Neue, Permanent Marker, Special Elite, Rock Salt, Unbounded e Bricolage/Space
  Grotesk/Syne variáveis — peso por `set_variation_by_axes`, Dela Gothic One, VT323, Press Start 2P, Silkscreen, Courier
  Prime). Teste em `becas-reels/estilos.py` → out/estilos.jpg (2 quadros de cada) + out/estilos_fontes.jpg (amostras e
  paletas): A COLAGEM (azul royal + papel amassado rasgado, letras recortadas cada uma numa fonte/papel, placa à mão,
  máquina de escrever, cena de jogo num rasgo), B TABULEIRO (roxo 88,58,232 com grão + lima 196,244,70 + creme, trilha de
  casas, "tarde de jogos" minúsculo em Unbounded 900, caixas como cartas de borda lima, vídeo dentro do tabuleiro), C TVs
  RETRÔ (noite com bokeh, TVs de madeira DESENHADAS — Pexels/Pixabay/Unsplash/Wikimedia bloqueados pelo proxy —, cenas de
  jogo nas telas com linhas de CRT, info em VT323 verde-fósforo e âmbar). Esperando ele escolher.
  **Ele pediu os 3 estilos como TRÊS VÍDEOS separados ("não mistura tudo"):** `becas-reels/v_colagem.py` (26,8 s: letras
  recortadas batendo com som de tesoura, cenas de jogo em rasgos de papel com tremidinho de stop motion, nome recortado +
  ficha datilografada, "ANOTA AÍ:" datilografado, estrela + placa "RESERVE NO WHATSAPP!", "COMENTA:"; batida de pisão e
  palma), `v_tabuleiro.py` (27 s: título em Unbounded, dados rolando a cada jogo, casa acesa andando na trilha, cena no
  meio do tabuleiro, "casa N: ..." em lima, carta lima com nome/ficha, cartas de info, "sua vez de jogar!"; marimba) e
  `v_tvs.py` (25,6 s: pilha de 6 TVs ligando, TV grande zapeando 6 canais com chiado e "CH 0N", info digitada em fósforo,
  pilha final com SINTONIZE / BECAS CAFÉ / WhatsApp / "QUAL CANAL VOCÊ VÊ?"; chiptune). Sons novos em `sons.py`.
- **Novas referências (4/nov): convite de feed, story e Reels da tarde no Becas.** Refs: "GAMES DAY!" (moldura de casas
  verde-água/mostarda/creme em volta de miolo bordô, figurinhas retrô com contorno escuro e sombra: explosão, raio, cartas,
  dados), "GAME NIGHT" anos 60 (grão, estrela atômica) e "GAME NIGHT" de letras de madeira tipo Scrabble em papel com
  bolinhas vermelhas e cartas de baralho na borda. **Opção 1 = `becas-reels/gamesday.py`** (post 6x7 casas, story 6x9; o
  texto do miolo se AJUSTA sozinho ao espaço (`miolo` procura a escala que cabe); caixas do acervo como adesivos de borda
  branca, guarda-chuvinha e xícara do Becas entre as figurinhas; Anton + Space Grotesk; `--reels` = 22 s: casas acendendo,
  figurinhas pulando, "TARDE DE JOGOS!", "NA MESA HOJE:" com 6 cenas de jogo no miolo, convite montando por blocos e pílula
  "COMENTA: QUAL JOGO VOCÊ QUER APRENDER?"; música retrô anos 60 (órgão, baixo andando)). **Opção 2 = `letrinhas.py`**
  (post e story: letras de madeira "TARDE / DE / JOGOS!" com pontos, Silkscreen para o texto, dados, pilha Hitster/Dixit/
  Telma, cartas desenhadas). Saídas em `becas-reels/out/gamesday/` e `out/letrinhas/`.
  **Ele corrigiu: NÃO misturar referências — cada referência vira o SEU conjunto (post + story + Reels) = 9 peças.**
  Ref 1 Games Day = `gamesday.py` (tirei a estrela atômica anos 60 do Reels; música própria `musica_funk`); ref 2 retrô
  anos 60 = `retro60.py` (verde-petróleo/laranja/mostarda/creme chapados, grão, estrelas atômicas, tabuleiro de hexágonos
  com árvores/ondas/montanhas, leque de cartas, dados, xícara laranja com zigue-zague, lápis, folha de pontos com as
  informações; Archivo Black; Reels: título letra a letra, peças entrando, "NA MESA:" com as cenas como cartões-postais,
  "COMENTA" entre o título e o tabuleiro; `gamesday.musica_retro`); ref 3 letras de madeira = `letrinhas.py` (Reels:
  letras caindo com batida de madeira, cenas dentro de cartas de baralho com o nome digitado em pixel, info digitada;
  `sons.musica_cafe`). Chat aceita no máx. 30 MB: comprimir em 2 passadas se passar.
- **Wonderland's War em PRIMEIRA PESSOA (`wonderland-reels/`, 4/nov, ideia dele):** "como se o jogador pusesse óculos de
  realidade virtual e entrasse no jogo", andando pelo tabuleiro e fazendo ações reais; no fim a pessoa só abre o olho,
  sentada na mesa com os outros, e fala "esse jogo é muito bom!". Edição BR = **Galápagos** (API `ccstore/v1/products/WLW001`:
  caixa 3D, tabuleiro montado em perspectiva, standees, meeples, verso; 1715x2000 mas a foto é pequena por dentro). Site: Deluxe
  R$ 60 / 7 dias, 2–5 jogadores, 125 min. Regras conferidas (rulespal): 3 rodadas = Chá Maluco (move o líder no sentido horário
  até uma cadeira livre e pega a carta: apoiadores numa região, aliados, fragmentos...; passar pela cabeceira = rola o dado de
  fragmentos e repõe as cartas; com 4 cartas o líder vai para uma das 5 regiões) + Guerra (em cada região todos puxam fichas
  do saco ao mesmo tempo; Loucura = perde unidades; para quando quiser (mão vazia); quem tem mais força ganha o prêmio e um
  castelo; forja). Líderes: Alice, Chapeleiro Maluco, Rainha Vermelha, Jaguadarte, Gato de Cheshire.
  **Teste da câmera em 1ª pessoa** (`pov.py`: tabuleiro retificado por homografia + Real-ESRGAN x4 `ampliar_tab.py`, projeção
  em plano com névoa e céu, standees como cartazes, moldura de óculos VR com HUD): de cima fica ok, mas PERTO do tabuleiro
  vira borrão (a foto oficial é pequena) e o recorte dos standees (GrabCut + rembg) sai sujo. Proposta: eles FILMAM as ações
  em 1ª pessoa no tabuleiro deles (lista de tomadas mandada no chat) e eu ponho HUD de VR, transições e o final.
  **Ele respondeu só "faz o vídeo"** (sem gravação no Drive) → `wonderland-reels/vr.py`, tudo digital, 51 s, sem narração:
  gancho "E SE VOCÊ ENTRASSE DENTRO DO JOGO?" com a lente dos óculos ligando → mergulho na boca do Gato da capa → descida
  até o tabuleiro → Festa do Chá (cartas Torre Vermelha/Morsa voando para 4 casas de inventário) → Floresta Tulgea com
  marcadores de apoiadores → GUERRA (fichas = arte do aliado num círculo, barras de força, Fragmento de Loucura com glitch,
  mão vazia = parou, VITÓRIA + castelo) → "3 RODADAS" → DESCONECTANDO → olhos abrindo (pálpebras + piscada) no "mundo
  real" (bokeh quente + caixa) com "...ESSE JOGO É MUITO BOM!" → "qual líder você seria?" → CTA (Deluxe 7 dias).
  A câmera fica ALTA (h ≥ 1650 px do tabuleiro_x4, `CHAVES`): de perto borra. Artes em `assets/artes/` (ampliadas x4); a
  Criatura saiu (o selo "1 Escolha seus aliados" cobre a arte) e o meeple recortado ficou deformado (não usar).
  Quando eles gravarem o final de verdade (abrir o olho na mesa e falar a frase), trocar `cena_sai` depois de T_OLHO pelo clipe.
  **8/nov: ELES GRAVARAM o tabuleiro (`wonderland-reels/brutos/mesa.mp4`, Drive de brutos 20261108_125410, 32 s, câmera
  rente à mesa) e pediram "primeira pessoa, mas APAGA O FUNDO, mexe bastante".** `mascara_mesa.py` (→ out/mask_mesa +
  out/obj_mesa, 360x640, ~15 min): borda do tabuleiro = RETA (RANSAC) onde a "sala" (claro e pouco saturado; sacola
  verde-água) acaba, ignorando colunas em cima de peças; acima da reta é fundo, MENOS as peças em pé do isnet (rembg
  isnet-general-use acha Alice/Gato/meeples perfeito, mas apaga o tabuleiro: serve só pras peças; cadeira = componente
  vazado, sai). Nos quadros 540–700 (trilha de pontos com cadeira atrás) a reta preferida é a de BAIXO. `pov_mesa.py`
  (44,8 s): gancho com a lente ligando → trechos do bruto com o céu do País das Maravilhas (degradê roxo, sorriso do
  Gato da capa como lua, estrelas e cartas oficiais flutuando com paralaxe do movimento da câmera, luz rosa no
  horizonte), HUD VR com MIRAS que seguem as peças (caixas do isnet suavizadas) e regras em painéis → "DESCONECTANDO" →
  abre o olho na MESMA mesa com a sala de verdade + "...ESSE JOGO É MUITO BOM!" → comenta e CTA do `vr.py`.
  **REJEITADO (9/nov): "ficou horrível".** Ele pediu um PROMPT pro Gemini (Veo) fazer o voo em 1ª pessoa a partir de
  UMA FOTO do tabuleiro (mandei 3 prompts em inglês: mergulho na Festa do Chá, voo rasante até a Alice, giro no Gato).
  Ao receber os clipes: montar como a série "a caixa ganha vida" (`serie_caixa.py`), sem recorte de fundo.
- **3 Reels "chama a Sua Vez pro seu evento de fim de ano" (`festa-reels/`, 5/nov, pedido dele: "seja criativo, não use a
  mesma coisa de sempre"; ele pediu os TRÊS e liberou voz de IA "se precisar"):** base `comum_festa.py` (cenas REAIS deles
  via `becas-reels/kit.py`, entrega com som / para música a −15,5 LUFS). `previsao.py` = PREVISÃO DO TEMPO da
  confraternização (estúdio azul de telejornal, AO VIVO, mapa do SALÃO DA FESTA com mesa do amigo secreto/buffet/pista/
  cantinho do celular, nuvem + neve + frente fria "90% de chance de climão", "rajadas de celular", ALERTA, frente quente com o
  logo, "imagens do satélite" = cenas deles, cartões jogos/monitoria/ABC+SP, mapa de sol "100% de risada", cartão final;
  narração edge-tts Antonio +10% em `voz/` (fora do git), legenda tipo closed caption; 40 s). `grilos.py` = O SILÊNCIO DA
  FESTA (tela escura, legendas de som [grilos] [alguém tosse] [garfo raspando no prato], medidor de ANIMAÇÃO quase zerado,
  dado rolando → "...ATÉ ALGUÉM CHAMAR A SUA VEZ" → cortes secos com as cenas deles e o medidor subindo até 100%; sem
  narração; 25 s). `lista.py` = A LISTA DA FESTA (folha de caderno na mesa de madeira, caneta escreve e marca ✓ comida,
  música, amigo secreto, decoração; no último item "fazer a galera se divertir junta (sem celular)" rabisca ???; carimbo
  "RESOLVIDO: CHAMA A SUA VEZ!"; polaroides com as cenas deles; post-its; 23 s). Fatos: ABC Paulista + SP capital,
  WhatsApp (11) 97793-3910, "a gente leva os jogos e fica o evento todo ensinando"; nada de "já atendemos".
- **TARDE DE JOGOS NO BECAS FECHADA (5/nov):** **sexta, 20/11/2026 (feriado), das 13h às 19h**, Becas Café, **Rua Sorocaba,
  35 – Mauá (CEP 09370-150; endereço do Restaurant Guru, pedi para ele confirmar)**; R$ 30 com R$ 15 de consumação; monitoria
  (eles levam os jogos e ensinam); cupom de 10% no 1º aluguel (BECAS10, precisa ser criado no site). Constantes `DATA` e
  `ENDERECO` + `selo_data`/`selo_endereco` em `promo/tarde_becas.py` (usadas também em `becas-reels/tarde.py`); horário de
  término: 19h (todas as peças dizem "13H ÀS 19H"). Kit: post, story, **flyer A5** (`flyer()`: o post + caixa com QR do site, 300 dpi,
  PNG + PDF), cupons A4 e o Reels das guarda-chuvinhas. Os 3 estilos alternativos (gamesday, retro60, letrinhas) também
  ganharam data e endereço (post, story e Reels).
  **Controle de ingressos (sugestão aceita):** venda antecipada por Pix no WhatsApp + planilha (sem Pix não é reserva), na porta
  lista + pulseira; cada pagante recebe DOIS cartões 9x5 cm (ele notou que o vale fica no caixa e o cupom se perderia): `vale(n)` QUADRADO 5x5 cm, fundo BRANCO com linha de corte cinza (pedidos dele: menor, 20 por A4, sem fundo amarelo) NUMERADO 001–060 (`vales_A4_001-060.pdf` = 3 folhas COMPLETAS, pedido dele; + em branco) = VALE CONSUMAÇÃO R$ 15 no Becas em 20/11 (entregue
  no caixa; conferir nº com a lista) e `cupom()` que a pessoa LEVA (também 5x5 cm, 20 por A4, QR ~2,1 cm lido no teste) = 10% OFF no 1º aluguel (BECAS10) + QR do site (conferido com o leitor do OpenCV); `cupons_A4.pdf` = 3 folhas de 20 = 60.
- **LISTA DE JOGOS da Tarde no Beca’s (6/nov, 30 jogos, fechada com ele):** Bananagrams, boop., Break the Cube, Canvas, Código
  Secreto: Imagens, Coffee Rush, Dixit, Dobble Disney (NÃO está no site), Draftosaurus, Drácula vs Van Helsing, Flip 7: A
  Vingança, Go Cuckoo!, Gravity Superstar, Hitster (levar 2 das 3 edições, 1 tocando por vez), Hive, King of Tokyo, Marrakech,
  Eu Sou uma Banana, Santorini, Say my Name, Splendor Duel, Spyfall, Sushi Go!, Taco Gato Cabra Queijo Pizza, Take Time, Tapalavras, Telma,
  The Mind, Uga Buga, Wandering Towers. Ele TIROU: Ref!, Last Message (→ Break the Cube), Next Station (→ Wandering Towers), Perfil Express e Splito ("muito confuso") (→ Eu Sou uma Banana), Tesouro do Dragão, Patchwork, Azul Duel, Cartógrafos, BraveRats e 1, 2, 3, Lucha! (→ Taco Gato Cabra Queijo Pizza), Spot it! Hip (→ Dobble Disney).
  Eu deixei de fora: Throw Throw Burrito e Happy Salmon (barulho/coisa voando no café), jogos de bebida e +18, jogos longos.
- **Stories ENQUETE "qual é o plano pro fim de semana?" + 1 jogo por plano (`promo/story_plano_fds.py`, 6/nov, ideia dele):**
  tela 1 = pergunta (petróleo com confete) + espaço LIVRE y≈930–1400 para a enquete (4 opções). Depois 1 story por plano:
  fundo de cor com confete, "SEU PLANO:" + plano, cartão branco com caixa oficial, nome, ficha e UMA frase, "RESERVA ESSE
  JOGO AQUI:" + seta e espaço LIVRE y≈1255–1490 para o adesivo de LINK do jogo no site. Planos: almoço em família → Dixit: Disney Edition (ele trocou o Dixit normal),
  date → boop., galera → Hitster, festa da empresa → Código Secreto: Imagens. **Rejeitado:** conceito "receita médica"
  (Dr. Sua Vez, Rx, carimbo) — ele não curtiu e achou informação demais; link embaixo (y≈1650) ficou baixo demais; saíram
  "ficar de boa em casa" (Canvas), "visita na sogra" (Take Time) e o Uga Buga na família. Saída `promo/out/plano_fds/`.
- **Gravações NO BECA'S (6/nov, pasta "Becas" no Drive `1KPZeiKXElsWPe9eagnIIW7utvZ6II15e`, liberada por link) →
  `becas-reels/brutos/nov06/` (fora do git), todos verticais HEVC com áudio ambiente: 150333 (15,6 s, entrada pelo jardim →
  guarda-chuvinhas → salão de madeira → Jéssica sentada a 14–15 s), 150657 (11 s, vitrine: torta, brownies, cookies),
  150936 (16 s, cardápio "Bem-vindo(a) ao Beca's", plástico brilhando, mostra preços), 151125 (57 s, CAMINHO: igreja
  grande de pedra com escadaria (nome a confirmar) → calçada "ESCOLAR" → farmácia Alquifarma → rua → bandeira e portão do
  Beca's → guarda-chuvinhas → salão), 151353 (6 s, brownie com chantilly e morango + Jéssica comendo, careta). Há clientes
  e uma criança no fundo de alguns planos: evitar close nos rostos deles.
  **As 4 peças (`becas-reels/no_becas.py <revela|chegar|gostinho|fotos>`, 6/nov, ele: "faz todos", cuidado com ROSTOS e
  PLACAS):** `revela` (14,7 s, pro sábado ao meio-dia: a carta "?" do save_date_sv vira e ABRE em tela cheia com o vídeo →
  bandeira/portão → guarda-chuvinhas → "TARDE DE JOGOS NO BECA’S CAFÉ!" com data, endereço, preço e "garanta sua mesa aqui:"
  + seta; y≈1350–1580 LIVRE pro adesivo de link; WhatsApp embaixo), `chegar` (22,3 s, barrinha de GPS IGREJA → ALQUIFARMA →
  BANDEIRA → BECA’S, etiquetas na hora certa, fecha com o cartão do convite + "salva esse vídeo"), `gostinho` (24,4 s:
  guarda-chuvinhas, salão, vitrine, cookies, brownie, careta da Jéssica com carimbo APROVADO, "agora imagina isso com um
  jogo na mesa..." com Dixit/Hitster/Telma pousando na mesa dela, convite + "qual doce você pede primeiro?") e `fotos`
  (carrossel 1080x1350, 5 telas: capa com o teto, portão, vitrine, brownie, convite). **Privacidade:** do caminho (151125)
  só entram 0–5,5 s, 12–24,4 s e 39–46 s (placas legíveis: Clio 6–11 s, van 25,5–29,5, HB20 30–35,5, carro preto 36–37;
  salão cheio com mulher e criança 55–57 s); `BORRA` (caixas com borda suave, tempo do bruto) na porta da igreja, num carro
  atrás do portão, na cliente atrás da Jéssica (a câmera gira: caixas em 3 faixas de tempo para não pegar o rosto DELA), na
  atendente atrás dos cookies e na equipe ao fundo do brownie; `TILT` = desfoque abaixo de y (teto, salão) onde há clientes.
  Cardápio não usado. Saída `out/{revela,chegar,gostinho}_{com_som,para_musica}_final.mp4` e `out/conheca_becas/`.
  **7/nov, ele: "borrou demais, ninguém se importa de aparecer no vídeo; no máximo um rosto ou outro, ficou horrível"** →
  TILT desligado e `BORRA` só na cliente de perto atrás da Jéssica. Regra: em vídeo do lugar, NÃO borrar gente ao fundo
  nem salão; placas de carro continuam evitadas pela escolha dos trechos. Os finais de 22–25 s passam de 30 MB: para o
  chat, x264 2 passadas a 8000k → `out/chat/` (~22–25 MB; o 1º envio de 32 MB não chegou pra ele).
  **A igreja do caminho é a IGREJA MATRIZ de Mauá** (Paróquia Matriz Imaculada Conceição, Praça Monsenhor Alexandre
  Venâncio Arminas, 1, bem no centro; ele confirmou "matriz"). 2ª rodada: "COMEÇA NA IGREJA MATRIZ", GPS com MATRIZ, pílula
  "PERTINHO DA IGREJA MATRIZ, NO CENTRO DE MAUÁ", e os 3 formatos: `revela_reels`, `chegar_stories`, `gostinho_stories`
  (+ os padrão) e o carrossel `out/como_chegar/` (capa + PASSO 1–4: Matriz, Alquifarma, bandeira verde, portão branco +
  "ANOTA AÍ: RUA SOROCABA, 35"), cada carrossel com `stories/story_NN.png`.
  **3ª rodada (7/nov):** (1) "como chegar" com o caminho INTEIRO (0–56,8 s a 2,7x, `C_VEL`; etiquetas por tempo do bruto em
  `C_SRC`) e as placas com desfoque PEQUENO que acompanha o carro (`TRILHAS`: keyframes medidos a 4 q/s; Clio, van escolar,
  HB20, carro preto) + só o rosto da cliente sentada no salão (55–57 s; a criança está de costas); (2) é **BOLO NUVEM** com
  morango (não brownie) no vídeo e no carrossel; (3) o gostinho NÃO fecha mais na Jéssica séria (eles não gostaram): fecha
  na mesinha redonda vazia do pátio (150333 a 2,5 s, quadro parado) com as caixas pousando no tampo (`G_MESA`).
  **Opções NOVAS** (`becas-reels/cafe_e_jogo.py combo|metade [--stories]`, sem mexer nas outras): "café + jogo = combo"
  (corte seco café ↔ jogo de mesa deles, "+" estourando: salão+Art Society, vitrine+Critter Kitchen, bolo nuvem+Sushi Go,
  teto colorido+Canvas; ele vetou o "portão" como benefício) e "metade café, metade jogo" (tela dividida). O vídeo da PAREDE do café (Jéssica) ainda não chegou no
  Drive: salvar como `brutos/nov06/parede.mp4` que ele entra sozinho no gancho e no par "uma parede dessas" + Passaporte.
  **ROTEIRO DELE "tarde comum → experiência" (`becas-reels/tarde_comum.py [--stories]`, 7/nov, ~36 s):** gancho com a
  pergunta "Você é do time que vai à cafeteria só pelo café... ou também pela diversão?" (teto colorido) → ambiente
  (salão, pátio) "Já imaginou transformar uma tarde comum...?" → desejo (capa do cardápio, vitrine, cookies, bolo nuvem)
  "Um café gostoso..." → VIRADA com match cut em ÍRIS (`iris()`: a placa redonda com a XÍCARA do logo abre na mesa do Art
  Society; a mesinha vazia do pátio recebe as caixas) "...uma mesa cheia de possibilidades..." → experiência (prato do bolo
  → íris → carta de doce do Sushi Go; Unlock abrindo, mãos no Sky Team, fichas do Critter, cartas do Canvas, Take Time)
  "...e boas histórias pra contar!" → tela dividida café/jogo "Café, jogos e boas companhias." → "VOCÊ VEM?" + convite.
  NÃO há gravação de xícara sendo servida nem de dado rolando: se gravarem no dia (3 s de café chegando à mesa), entra no lugar da placa.
  **2ª versão (7/nov, "você repetiu muito os vídeos"):** cada trecho entra UMA vez. Achei 2 brutos do Beca’s que eu NÃO
  tinha usado (a listagem do Drive vem paginada: SEMPRE listar tudo, ex. `title contains '20261106'`): **150726** (8,8 s:
  a PAREDE pintada "Beca’s Café" com pés de café 0–5 s, teto e saída pro pátio 5–8 s) e **151311** (26 s: colher no bolo
  nuvem 0–4 e 18–21, a Jéssica comendo 5–7 e rindo com a colherada que a criança de rosa dá 22–24; o rosto da criança
  aparece de perto em 15–17 e 25 s: evitar). Gancho agora na parede; chegada da rua (bandeira, 36,6 s a 2x); a Jéssica
  rindo na tela dividida do fim; fundo do convite = a parede.
  **3ª (7/nov):** ele achou longo e "tosca" a montagem da mesinha com as 3 caixas → SAIU (38,3 s). **Ele vai NARRAR:**
  gravador `becas-reels/gravador/Gravar_narracao_Tarde.html` (7 falas = os textos da tela + "Você vem? ... Garante a sua mesa
  pelo WhatsApp!", arquivos `becastarde_narracao_NN`):
  `https://raw.githack.com/erik-magalhaes/GitJoy/7442d9b78b8abeeba5573e597b99084324b54a3e/becas-reels/gravador/Gravar_narracao_Tarde.html`.
  **4ª (7/nov):** saiu o plano da mãozinha da criança com a colher no bolo (151311 18–21 s); no lugar, com a mesma
  duração (38,3 s), a página "Bem-vindo(a) ao Beca’s Café" do cardápio (150936 3,4 s), que abre em íris na carta do Sushi Go.
  **NARRAÇÃO RECEBIDA (7/nov):** 6 dos 7 .webm (FALTA a fala 6, "Café, jogos e boas companhias."): `narracao_tarde/raw/`
  → ffmpeg com a cadeia de voz a 44,1 kHz (`tmp_NN.wav`) → `tratar_tarde.py` (funções do `taco-reels/tratar_narracao.py`;
  o `corta_resto_respiro` comia o "Um" da fala 3, então ele só vale se tirar < 0,3 s; o faster-whisper desta máquina falha
  com caminho de arquivo (`av.open(metadata_errors)`): passe o áudio como array float32 a 16 kHz). Em `tarde_comum.py` cada
  fala entra no começo do seu bloco (`VOZ_EM`), o gancho e o convite esticam para a fala, a etiqueta "...ou também" entra no
  "ou" e o cartão do convite no "tarde"; a voz é somada DEPOIS da mixagem (`poe_voz`, sem o tanh) e a trilha abaixa sob ela.
  Para compensar, encurtei a rota da chegada e 3 planos do desejo: **41,9 s**. Ele falou "E aí, você vem?" e "Garanta".
  `--sem-legenda` tira os textos falados. Quando a fala 6 chegar: tratar e renderizar de novo (a tela dividida estica sozinha).
  Ao receber: tratar a voz, esticar/encolher cada bloco de cenas (TEXTOS) para a fala, legenda pela fala real.
- **MAPA "COMO CHEGAR DE TREM OU ÔNIBUS" (`becas-reels/mapa_becas.py`, 7/nov, pedido dele: "como o Google Maps, só que
  sketch, colorido, bonitinho"):** ruas REAIS do OpenStreetMap (`mapa/area.osm`, baixado da API 0.6 `map?bbox=`; o Overpass
  falha pelo proxy; Nominatim funciona) desenhadas à mão: traço tremido (`treme`), lápis de cor em hachura, avenidas amarelas,
  trilhos da Linha 10-Turquesa com dormentes, praças verdes, estação/terminal/Matriz pintados, nomes das ruas em Patrick Hand.
  Rota a pé = menor caminho no grafo das ruas (`mapa/rota.py`): **Estação Mauá (entrada sul) ≈ 200 m, uns 3 min**; **Terminal
  Municipal de Mauá ≈ 340 m, uns 4 min** (passa pela estação e desce a Rua da Matriz até a Rua Sorocaba). O Beca’s (nº 35)
  ficou perto da esquina da Rua Santa Cecília (o nº 69 é a Biomed; a Alquifarma é Santa Cecília 276): posição APROXIMADA.
  Ícones OpenMoji (`mapa/openmoji/`, SVG → PNG com cairosvg) em selos redondos; rota = bolinhas azuis do Maps; pin vermelho
  com a xícara + "CHEGOU!"; barra de busca "Beca’s Café · Rua Sorocaba, 35" e painel de baixo "COMO CHEGAR de trem ou
  ônibus". Saídas `out/mapa/`: `mapa_post.png` (1080x1350), `mapa_story.png` (espaço do adesivo "ABRE A ROTA NO SEU MAPS
  AQUI:" para ele pôr o link do Maps) e o vídeo de 12 s (`--reels` / `--stories`: o mapa se desenha, os ícones pulam, o
  bonequinho anda pela rota, o pin cai, o painel sobe).
  **2ª rodada (7/nov, "ficou muito longe, não dá pra entender"):** zoom de 0,46 → 0,33 m/px: o mapa ficou GIRADO 20° no
  sentido horário (`ROT`, com bússola apontando o norte) para a rota terminal → Beca’s ficar na diagonal da tela, e a faixa
  "TARDE DE JOGOS" desceu para a borda do painel (libera o alto). `enquadra()` centra rota + ícones na faixa visível; as
  etiquetas nunca saem da tela (Terminal acima do ícone, Matriz abaixo, fora do pin). No vídeo, o "VEM DE TREM OU DE
  ÔNIBUS?" fica embaixo do mapa até o painel subir.
- **"UM CAFÉ... NUM CAFÉ?" com a capa do Coffee Rush ANIMADA no Gemini (`becas-reels/cafe_rush.py`, 7/nov, ideia dele):**
  eu escrevi o prompt do Veo (em inglês: capa ganha vida → câmera entra na vitrine → caixa numa mesa de café real com
  xícara fumegando e guarda-chuvinhas coloridas no teto; SEM texto, só som de café) e fiz a imagem inicial vertical
  `coffee-reels/out/coffee_rush_9x16.png` (caixa oficial Galápagos em fundo creme). **O Gemini devolveu 720x1280, 24 fps,
  10 s** (`coffee-reels/brutos/gemini1.mp4`, fora do git): ele usou a foto QUADRADA com fundo transparente → bordas pretas
  nos 4 primeiros segundos (`tira_preto`: preto ligado à borda vira creme); no meio o Gemini REDESENHOU a cena da capa (não é
  a arte oficial) e de 7 a 10 s a caixa está numa mesa de madeira com as guarda-chuvinhas (ótimo). Reels: gancho "JÁ PENSOU
  EM JOGAR UM CAFÉ... NUM CAFÉ?", "O COFFEE RUSH VAI ESTAR NA MESA!" + data, convite da tarde (como o `tarde_comum`) e
  "COMENTA: CAFÉ PRETINHO OU COM LEITE?"; som = ambiente do próprio clipe + `musica_cafe`. 15,6 s, `--stories` com o link.
  **Série "A CAIXA GANHA VIDA" (ele aprovou, 7/nov):** capa animada no Gemini → personagem sai da caixa pro mundo real →
  "aluga e leva pra casa". Funciona melhor com capa de POUCOS personagens grandes, uma ação por vídeo, imagem inicial 9:16 com
  fundo creme (nunca quadrada/transparente) e SEM texto no prompt. Episódios 2 e 3 mandados: **King of Tokyo** (caixa 3D Devir
  de `hobby-reels/assets/caixas/`) e **boop.** (foto do site recortada; sobra laranja tirada por cor ligada ao fundo) →
  `coffee-reels/out/{king_of_tokyo,boop}_9x16.png` (fora do git; refazer: caixa 900 px de largura no degradê creme +
  sombra). Ideias seguintes: Wingspan, Sushi Go!, Ticket to Ride, Dixit, Draftosaurus, Flamecraft.
  **Montagem: `becas-reels/serie_caixa.py <king|boop> [--stories]`** (EPS: clipe do Gemini em `coffee-reels/brutos/`,
  gancho, texto do meio, "comenta"): 10 s do clipe + gancho no alto + texto quando o bicho já saiu + tela final de ALUGUEL
  (caixa recortada, `card_aluguel` com logo PEQUENO (190 px; com 230 encavalava no título), "ALUGUE O ...", ficha do `acervo_site.json`, R$ e 5 dias, retirada em Mauá ou
  entrega, link na bio) e "comenta"; Stories com "aluga aqui:" + espaço do link. King of Tokyo (`gemini2.mp4`, 10 s,
  720x1280): o lagarto sai da caixa e pousa na mesa da sala com os dados — ótimo de primeira.
  **boop. (`gemini3.mp4`) veio DEITADO (1280x720)** mesmo com a imagem em pé: `deitado=True` troca o `K.GRADE` por um
  filtro que põe a cena inteira no meio (altura 760) sobre o próprio vídeo desfocado (nada cortado). Os gatinhos saem da
  caixa e se empurram na cama.
  **8/nov: ele faz 3 por dia no Gemini.** Mandei imagens + prompts de mais 5, nesta ordem: 1 Wingspan (pássaro voa até a
  estante), 2 Ticket to Ride (trem sai e anda no mapa até a mesa; caixa = foto do SITE, arte antiga), 3 Draftosaurus
  (MeepleBR, `gravados-reels/assets/oficial/`; dinos num parquinho na mesa), 4 Dixit (cartas voam como portas de sonho
  até a mesa do Beca’s com guarda-chuvinhas = episódio que fecha com o CONVITE da tarde, como o Coffee Rush), 5 Flamecraft
  (dragãozinho acende as lâmpadas das lojinhas; Deluxe R$ 60 / 7 dias) → `coffee-reels/out/N_<jogo>_9x16.png`.
  Ao receber cada clipe: `coffee-reels/brutos/geminiN.mp4` + entrada nova em `EPS` do `serie_caixa.py` (conferir se veio
  deitado). Dixit precisa da tela final do convite (copiar de `cafe_rush.py`).
- **CONVITE DOS MEEPLES (`becas-reels/convite_meeple.py`, 8/nov):** ele viu o modelo "Convite para festa" do Gemini (bicho
  de FELTRO abrindo envelope). A raposa do exemplo não tinha a ver → pediu **meeples** e depois **de MADEIRA (não feltro)
  segurando guarda-chuvinhas coloridas**. O modelo força feltro: usar o modo **Vídeos** normal + botão do formato em pé
  (9:16; é o botão do retângulo embaixo da caixa de texto — por isso o boop. veio deitado). Prompt: 2 meeples de madeira
  laranja e petróleo (cores do logo), guarda-chuvinhas de papel, café com guarda-chuvinhas no teto, envelope verde e
  cartão em BRANCO parado de frente nos últimos 3 s (o Gemini erra letra/acento; EU escrevo). `meeple_a.mp4` (madeira) é o
  usado; cartão imóvel de 7,3 s em diante em x 280–806, y 648–1364 (1080x1920). `meeple_b.mp4` = versão de feltro (sobra).
  Texto no cartão (parceria Sua Vez × Beca’s, TARDE DE JOGOS, data, horário, endereço, preço). 2ª rodada ("demorou
  muito pra aparecer, fica muito tempo a folha branca"): o texto já vem no papel que SOBE do envelope (6,0 s) e o
  acompanha: `mascara_cartao` acha o papel creme em cada quadro (topo/esquerda medidos, largura 460, altura pela razão do
  cartão) e o texto só aparece onde há papel (o envelope e os guarda-chuvinhas na frente escondem); de 6,8 s em diante usa
  o retângulo parado (292, 648, 793, 1362). 3ª ("o S de JOGOS some"): o guarda-chuvinha amarelo do meeple petróleo fica
  NA FRENTE da direita do cartão (de ~83% da largura, altura do título/data) e o rosa cobre o pé à esquerda → texto
  deslocado 28 px pra esquerda, título menor (86/70), pílula 372 px; 10–15 s
  quadro parado com aproximação lenta + WhatsApp/comenta (Reels) ou "garanta sua mesa aqui:" (Stories). NÃO usar
  `tira_preto` em clipe sem borda preta (ele "pintava" de creme o escuro do café na borda).
- **Mais material com GUARDA-CHUVINHAS (`promo/becas_chuva.py`, 5/nov):** ele disse que a arte das guarda-chuvinhas é a
  preferida ("combina com a estética do lugar") e pediu mais peças nessa linha. Ideia nova: os guarda-chuvinhas SEGURAM as
  coisas pelo cabo (`segura()`: fio do teto → guarda-chuva → argola → placa/caixa/número), como um móbile. Peças: stories de
  CONTAGEM (faltam 7/3/2 dias, É AMANHÃ!, É HOJE!; disco pendurado; espaço livre ~y 1610–1760 para o adesivo de link),
  carrossel 5 telas "PREVISÃO PRA SEXTA, 20/11: CHUVA DE JOGOS" (caixas chovendo, como funciona com 3 plaquinhas, caixas
  penduradas, etiqueta R$ 30 + cupom 10%, reserva) e PLAQUINHAS DE MESA 1–8 (A4 dobrada ao meio, uma cor por mesa,
  "Dúvida no jogo? Chama a gente!"). Marrom sobre contorno marrom fica ilegível no `E.titulo`: use cor clara.
- **STORY EM VÍDEO da Tarde no Becas (`becas-reels/story_becas.py`, 5/nov):** ele vai PROMOVER o Stories e quer vídeo com as
  guarda-chuvinhas, "pode ser narrado". 16 s: gancho "BORA JOGAR NUM CAFÉ?" → guarda-chuva grande segurando uma POLAROIDE
  com as cenas REAIS deles (troca a cada 1,15 s), tudo balançando como pêndulo (`pendulo()`: sprite com o pivô no centro,
  girado inteiro) → etiqueta R$ 30 pendurada → CTA com data, endereço, WhatsApp e "Manda pra quem vai com você!". Área
  segura de anúncio: nada importante acima de y≈300 nem abaixo de y≈1560. Narração = ELES gravam 4 falas
  (`gravador/Gravar_narracao_Story.html`, arquivos `becasstory_narracao_NN`); com `narracao_story/frase_NN.wav` o script
  estica cada cena para a fala, abaixa a trilha e põe legenda. Saída `out/story_becas_{com_som,para_musica}_final.mp4`.
- **LOGO DO CAFÉ (5/nov):** eles mandaram o logo: o nome é **"Beca’s Café"** (com apóstrofo; antes eu escrevia "Becas") →
  `promo/assets/logo_becas_orig.jpg` (verde-oliva, letras creme). `tarde_becas.logo_becas(h)` (cartão com contorno marrom e
  sombra, como o logo da Sua Vez) e `parceria(h)` (Sua Vez × Beca’s lado a lado) entraram no post, story, vale (topo),
  carrossel "chuva de jogos" (capa e reserva), stories de contagem (rodapé), plaquinhas de mesa (os 2 logos à direita), Reels
  das guarda-chuvinhas e story em vídeo. Os 3 estilos alternativos (gamesday, retro60, letrinhas) NÃO foram atualizados
  (eles seguiram com as guarda-chuvinhas).
- **CRACHÁS da monitoria (`promo/cracha.py`, 5/nov):** para economizar na camiseta, eles vão usar crachá no cordão.
  10 x 14 cm em pé (porta-crachá comum), 300 dpi, A4 com 4 (Erik, Jéssica e 2 com o nome em branco). 3 opções em
  `out/becas/cracha_opcoes.jpg`: A guarda-chuvinhas (logo, pílula MONITORIA, nome, "Dúvida no jogo? Me chama!", Sua Vez ×
  Beca’s), B CARTA DE JOGO (petróleo, carta creme com índice "SV", "CLASSE: MONITOR/MONITORA", habilidade especial), C bloco
  laranja listrado (MONITORIA enorme, nome em faixa branca, QR do acervo "Gostou do jogo? Aluga e joga em casa!").
  2ª rodada ("gostei, mas cria novas opções"): `cracha_opcoes2.jpg` = D INGRESSO STAFF (canhoto picotado "VALE 1 EXPLICAÇÃO
  DE JOGO", código de barras), E LETRAS DE MADEIRA tipo Scrabble (MONITOR e o nome em peças com pontos, papel de
  bolinhas), F TRILHA DE TABULEIRO na borda (casas coloridas, INÍCIO, "Travou no jogo? Não volte casas: me chama!").
  3ª rodada ("mais focado na Sua Vez, sem o Beca’s, pra usar em qualquer evento"): `cracha_opcoes3.jpg` = G azul-claro
  com confete, logo grande, "A gente ensina, você joga!"; H trocadilho "É A VEZ DE:" com setas apontando o nome, fundo
  amarelo listrado; I "equipe" (faixa petróleo com logo, nome em faixa laranja, QR do acervo). Sem data nem café.
  **Escolhida: C** (a Jéssica, 5/nov), com o nome em azul-petróleo CLARO (64,170,200) porque o petróleo escuro ficava difícil de ler → `cracha_C_A4.pdf`; só Erik + Jéssica (1 folha A4, os 2 lado a lado, pedido dele) → `cracha_C_Erik_Jessica.pdf` (`folha_a4(f, nomes)`).
- **SAVE THE DATE em vídeo para os Stories (`becas-reels/save_date.py`, 5/nov):** 10 s, guarda-chuvinhas balançando + um
  guarda-chuva rosa segurando uma FOLHA DE CALENDÁRIO (NOVEMBRO / 20, logos Sua Vez × Beca’s no pé, `SB.OBJ["cal"]`,
  escala `KC`) que balança; caneta vermelha circula o 20 (1,3–2,1 s); "SAVE THE DATE!", 3 pílulas (tarde de jogos no
  Beca’s, sexta (feriado) 13h às 19h, endereço) e "ativa o lembrete:" + seta. Área y≈1620–1790 LIVRE para o adesivo de
  contagem regressiva do Instagram (ele vai colocar). Do 3,5 s em diante só balança.
  **6/nov, virou TEASER (pedido dele): SEM o nome do café** (só o logo da Sua Vez no calendário), "SAVE THE DATE!", "VEM
  NOVIDADE POR AÍ...", "SÁBADO, AO MEIO-DIA, A GENTE CONTA TUDO!" e "ativa o lembrete pra não perder:"; o contador dele
  aponta para o sábado meio-dia (revelação do evento). Saída `out/save_date_{com_som,para_musica}_final.mp4`.
- **SAVE THE DATE — MISTÉRIO com a cara da Sua Vez (`becas-reels/save_date_sv.py`, 6/nov):** ele achou o das
  guarda-chuvinhas "muito na temática do café" e pediu algo da SUA VEZ, sem tarde de jogos, "sem nada", só mistério:
  "fica ligado, vem coisa boa; a novidade sai no sábado ao meio-dia" (ele põe o contador do Instagram). 10 s: azul-claro
  com trilha de casas e "?" flutuando, logo; CARTA DE JOGO virada (verso petróleo listrado com "?" amarelo) treme, vira e
  mostra NOVEMBRO / 20 / "ANOTA AÍ!"; "SAVE THE DATE!", "VEM COISA BOA POR AÍ...", "SÁBADO, AO MEIO-DIA, A GENTE CONTA
  TUDO!", "fica ligado: ativa o lembrete" + seta; área y≈1350–1560 (MEIO da tela) livre para o adesivo (7/nov: ele achou o espaço embaixo baixo demais; carta menor KC 0,78 e tudo subiu). Trilha marimba pop.
  Saída `out/save_sv_{com_som,para_musica}_final.mp4`.
