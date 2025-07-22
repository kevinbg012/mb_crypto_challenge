# MB Crypto Challenge

## Introdução

O projeto é um desafio do processo seletivo do Mercado Bitcoin, que consiste em uma implementação feito com FastAPI.

## Desafio

O desafio consiste em realizar algumas tarefas envolvendo gerenciamento de carteiras, ativos e interação com a blockchain.

No projeto temos funcionalidades como:
- Geração de carteiras a partir de uma frase mnemônica.
- Listagem dos endereços
- Validação de transação diretamente com Node Provider
- Geração de transações em ETH e algumas smart contracts ERC-20, como USDC, PYUSD e EURC

No projeto a rede blockchain utilizada é o Sepolia, uma testnet da Ethereum, e o Node Provider utilizado é o Infura.

### Endpoints

No projeto temos os seguintes endpoints:
- `GET /api/v1/address` - Listagem de carteiras
- `POST /api/v1/address` - Criação de job para geração de múltiplas carteiras
- `POST /api/v1/transactions` - Criação de transação
- `GET /api/v1/transactions/history` - Dado um endereço, retorna o histórico de transações
- `GET /api/v1/transactions/validate` - Validação de transação e persiste como histórico caso carteira esteja salva no sistema

Para mais detalhes de como utilizar a API, ao subir a aplicação, você pode acessar a documentação interativa da API 
em `http://localhost:8000/docs`.

### Como Usar

Uma vez tendo Docker em sua máquina, você pode iniciar o projeto com o seguinte comando na raiz do projeto:

```bash
docker compose watch
```

Caso queira recomeçar do zero, montar as imagens docker e voltar a ter o banco de dados limpo, você pode utilizar o seguinte comando:
```bash
docker compose down -v
```

### Acesso ao banco de dados

Caso queira acessar o banco de dados e tenha o psql instaldo, você pode utilizar o seguinte comando:

```bash
psql -h localhost -U postgres -d app
```

com password `changethis`.
