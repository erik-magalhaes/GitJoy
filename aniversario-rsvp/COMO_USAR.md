# Confirmação de presença do aniversário

A página tem o visual do convite (Lila Story, Toy Story). Para mudar o visual, edite `pagina.html` e rode
`python3 montar.py`, que gera o `Index.html` com as imagens de `img/` embutidas.

O convidado toca no link → abre uma página simples → "Vou!" ou "Não vou", nome, quantos adultos e crianças →
Enviar. A resposta cai sozinha numa Planilha Google sua (aba **Confirmações**), e a aba **Resumo** soma o total
de pessoas. Sem Google Forms e sem site de terceiros. Se a mesma pessoa responder de novo, a linha é atualizada.
Depois do prazo (15/11) o link avisa que as confirmações encerraram.

## Montar (uma vez, ~5 min; mais fácil no computador)

1. Abra **sheets.new** e dê um nome à planilha (ex.: "Aniversário – confirmações").
2. Menu **Extensões → Apps Script**.
3. Apague o que estiver no arquivo `Código.gs` e cole o conteúdo de **`Codigo.gs`** (os dados da festa da Lila
   já estão preenchidos no bloco `FESTA`, no topo).
4. Clique no **+** ao lado de "Arquivos" → **HTML** → nome **`Index`** → cole o conteúdo de **`Index.html`**.
5. Salve (ícone de disquete). Na barra de cima, escolha a função **`configurar`** e clique em **Executar**.
   O Google vai pedir autorização: **Revisar permissões → sua conta → Avançado → Acessar (não seguro) → Permitir**
   (o aviso aparece porque o script é seu, não de uma empresa verificada).
6. **Implantar → Nova implantação → engrenagem → App da Web**.
   - Executar como: **Eu**
   - Quem pode acessar: **Qualquer pessoa**
   → **Implantar** e copie o link (termina em `/exec`).
7. Abra o link no celular e faça um teste. Depois apague a linha do teste na aba Confirmações.

> Se mudar algo no código depois: **Implantar → Gerenciar implantações → lápis → Versão: nova → Implantar**
> (o link continua o mesmo).

## Mensagem do convite (WhatsApp)

Mande a imagem do convite e, logo depois (ou como legenda), o texto:

```
Você é nosso convidado pro aniversário de 2 anos da Lila! 🤠🚀
Confirme sua presença até 15 de novembro, é só tocar aqui 👇
[LINK /exec]
```
