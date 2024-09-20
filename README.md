<img align="right" alt="Mapa de Queimadas no DF" width="30%" height="auto" src="https://github.com/GabrielRF/Queimadas/blob/main/mapa.jpg?raw=true">

# Queimadas 🔥

Script python que monitora o site do INPE e envia mensagem no Telegram e/ou no Bluesky informando os pontos de queimadas.

Após ajustar as variáveis de ambiente, opte por executar o script python ou um container docker.

## Variáveis de ambiente
* `URL`: URL dos arquivos csv. Valor padrão: `https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/`;
* `FONTE`: Portal Queimadas do INPE. Valor padrão: `https://terrabrasilis.dpi.inpe.br/queimadas/portal/`;
* `GEOLOCATOR_AGENT`: Nome da aplicação - Valor livre;
* `TELEGRAM_TOKEN`: Token to bot do Telegram que fará os envios. Caso não seja preenchido, o script ignorará o envio para o Telegram;
* `TELEGRAM_CHATS`: IDs dos chats do Telegram que receberão as atualizações;
* `BLUESKY_USER`: Usuário do Bluesky;
* `BLUESKY_TOKEN`: Token de acesso / Senha de aplicativo do Bluesky. Caso não seja preenchido, o script ignorará o envio para o Bluesky;
* `HORAS`: Quantidade de horas a serem consideras na elaboração do mapa. Valor padrão: `6`;
* `ESTADO`: Unidade Federativa a ser considerada na elaboração dos mapas. Caso não preenchido, o script funcionará para todas as UFs;
* `MAPA_CENTRO`: Coordenadas do centro do mapa;
* `MAPA_ZOOM`: Nível de zoom do mapa;
* `MAPA_LARGURA`: Largura do mapa em pixels;
* `MAPA_ALTURA`: Altura do mapa em pixels;
* `LIMITE_NORTE`: Limite norte da área avaliada dos focos de queimadas;
* `LIMITE_SUL`: Limite sul da área avaliada dos focos de queimadas;
* `LIMITE_LESTE`: Limite leste da área avaliada dos focos de queimadas;
* `LIMITE_OESTE`: Limite oeste da área avaliada dos focos de queimadas.

## Execução

### Python

Para executar o script em python diretamente, primeiro instale os requisitos:

```
pip3 install -r requirements.txt
```

Feito isto, defina as variáveis de ambiente e execute o script usando:

```
python queimadas.py
```

### Docker

Crie o arquivo `docker-compose.yaml` com todas as variáveis necessárias. Utilize como exemplo o arquivo `docker-compose-sample.yaml`.

Execute:

```
docker-compose up
```
