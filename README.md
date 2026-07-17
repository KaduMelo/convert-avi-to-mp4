# convert-avi-to-mp4

Script em Python para converter vídeos `.avi` para `.mp4` sem perder qualidade.

## Como funciona

O script usa o `ffmpeg` por trás dos panos (via `subprocess`) e segue esta estratégia:

1. **Remux (padrão)**: primeiro tenta apenas trocar o container (`-c copy`), copiando os streams de vídeo e áudio sem recodificar. Se o vídeo do `.avi` já usa um codec compatível com MP4 (o mais comum é H.264), o resultado tem **qualidade idêntica ao original** e a conversão é quase instantânea.
2. **Recodificação sem perdas (fallback automático)**: se o remux falhar — porque o codec do AVI (ex.: DivX/Xvid) não é suportado dentro de um container MP4 — o script recodifica automaticamente usando H.264 com `CRF 0` (lossless) e áudio em FLAC. A qualidade visual não é perdida, mas o arquivo final fica bem maior.
3. Também é possível forçar o modo de recodificação sem perdas diretamente com a flag `--lossless`, pulando a tentativa de remux.

O script aceita tanto um arquivo `.avi` único quanto um diretório (nesse caso, converte todos os `.avi` encontrados recursivamente).

## Requisitos

- Python 3.8+ (já testado com Python 3.14)
- `ffmpeg` instalado no sistema (não é um pacote Python, é um binário do sistema)

### Instalando o ffmpeg

```bash
sudo apt install ffmpeg
```

Verifique a instalação:

```bash
ffmpeg -version
```

## Setup do projeto (venv)

O script usa apenas a biblioteca padrão do Python — não há dependências externas a instalar. Ainda assim, o projeto usa um ambiente virtual (`.venv`) para manter tudo isolado.

```bash
# Criar o ambiente virtual (só precisa fazer uma vez)
python3 -m venv .venv

# Ativar o ambiente virtual
source .venv/bin/activate

# (Opcional) instalar dependências — atualmente não há nenhuma
pip install -r requirements.txt
```

Para sair do ambiente virtual quando terminar:

```bash
deactivate
```

## Como usar

Com o `.venv` ativado (ou usando o Python do sistema, já que não há dependências):

### Converter um único arquivo

```bash
python3 convert_avi_to_mp4.py video.avi
```

Gera `video.mp4` na mesma pasta do arquivo original.

### Converter todos os `.avi` de uma pasta (recursivo)

```bash
python3 convert_avi_to_mp4.py pasta_de_videos/
```

### Especificar uma pasta de saída diferente

```bash
python3 convert_avi_to_mp4.py pasta_de_videos/ -o pasta_de_saida/
```

### Forçar recodificação sem perdas (pular tentativa de remux)

```bash
python3 convert_avi_to_mp4.py video.avi --lossless
```

Use essa opção se você sabe que o remux vai falhar (ex.: vídeos antigos em DivX/Xvid) e quer pular direto para a recodificação, ou se quiser garantir uma recodificação completa por algum outro motivo.

### Ver todas as opções

```bash
python3 convert_avi_to_mp4.py --help
```

## Estrutura do projeto

```
convert-avi-to-mp4/
├── convert_avi_to_mp4.py   # script principal
├── requirements.txt        # dependências Python (nenhuma no momento)
├── .gitignore               # ignora .venv/, arquivos .avi/.mp4, etc.
└── README.md
```

## Observações sobre qualidade e tamanho de arquivo

- O modo **remux** é sempre preferível quando possível: zero perda de qualidade e conversão quase instantânea, pois não recodifica nada.
- O modo **lossless (CRF 0)** garante que não há perda de qualidade perceptível, mas gera arquivos significativamente maiores que uma compressão "normal" — é o preço de não perder qualidade nenhuma.
- Se o objetivo for reduzir o tamanho do arquivo aceitando uma perda de qualidade mínima (praticamente imperceptível), seria necessário usar um CRF maior (ex.: 18), o que não é o comportamento padrão deste script, já que o objetivo é preservar a qualidade original.
