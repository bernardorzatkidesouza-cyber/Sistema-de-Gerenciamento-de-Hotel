# Documento Técnico — Sistema de Gerenciamento de Hotel

## 1. Visão geral

O sistema é um back-end dividido em **quatro microsserviços independentes**, escritos em Python com Flask. Cada serviço tem seu próprio processo, sua própria porta e seu próprio banco SQLite. Os serviços se comunicam apenas por HTTP/JSON. Nenhum serviço acessa o banco de outro.

| Item | Tecnologia |
|---|---|
| Linguagem | Python 3 |
| Framework web | Flask 3 |
| ORM / banco | Flask-SQLAlchemy 3 + SQLite (um arquivo `.db` por serviço) |
| Comunicação entre serviços | `requests` (HTTP síncrono, timeout de 5 s) |
| Servidor em produção | Gunicorn |
| Hospedagem | Render (um Web Service por microsserviço) |
| Testes manuais | Extensão REST Client do VS Code (`rest-client/*.http`) |

## 2. Arquitetura

```
                 ┌────────────────────┐
                 │  servico_hospedes  │ :5001  hospedes.db
                 └─────────▲──────────┘
                           │ (1) GET /api/hospedes/<id>
┌────────────────────┐     │
│  servico_reservas  │─────┤ :5003  reservas.db
└─────────▲──────────┘     │ (2) GET /api/quartos/<id>/disponibilidade
          │                ▼
          │      ┌────────────────────┐
          │      │  servico_quartos   │ :5002  quartos.db
          │      └────────────────────┘
          │ (3) PUT /api/reservas/<id>/status
┌─────────┴──────────┐
│ servico_pagamento  │ :5004  pagamentos.db
└────────────────────┘
```

### 2.1 Organização interna de cada serviço

| Arquivo | Responsabilidade |
|---|---|
| `app.py` | Cria a aplicação Flask, configura o banco, registra rotas, `/api/health` e os tratadores de erro. |
| `models.py` | Define a tabela do serviço (modelo SQLAlchemy) e a conversão para JSON (`para_dict`). |
| `rotas.py` | Blueprint com os endpoints HTTP; apenas recebe a requisição e devolve a resposta. |
| `regras.py` | Regras de negócio e validações; é onde as integrações são chamadas. |
| `integracao.py` | Função `chamar()` usada para falar com outros serviços (URLs, timeout e tratamento de falhas). |
| `erros.py` | Exceções `RegraDeNegocioError` (erro do usuário, 4xx) e `ErroIntegracao` (falha de outro serviço, 5xx). |
| `requirements.txt` | Dependências do serviço, usadas pelo Render. |

## 3. Modelos de dados

IDs de outros serviços são guardados como números comuns, **sem ForeignKey**, porque cada serviço tem um banco separado.

### Hóspede (`hospedes.db`)
| Campo | Tipo | Regras |
|---|---|---|
| id | inteiro | chave primária |
| nome | texto (120) | obrigatório |
| cpf | texto (14) | obrigatório, **único** |
| telefone | texto (20) | obrigatório |
| email | texto (120) | obrigatório, **único** |
| endereco | texto (200) | obrigatório |

### Quarto (`quartos.db`)
| Campo | Tipo | Regras |
|---|---|---|
| id | inteiro | chave primária |
| numero | inteiro | obrigatório, positivo, **único** |
| tipo | texto (40) | obrigatório |
| capacidade | inteiro | maior que zero |
| valor_diaria | decimal | maior que zero |
| status | texto | `disponivel` ou `indisponivel` |

### Reserva (`reservas.db`)
| Campo | Tipo | Regras |
|---|---|---|
| id | inteiro | chave primária |
| hospede_id | inteiro | ID do serviço de hóspedes (validado por integração) |
| quarto_id | inteiro | ID do serviço de quartos (validado por integração) |
| data_entrada / data_saida | data | formato `AAAA-MM-DD`; saída posterior à entrada |
| valor_total | decimal | calculado: `valor_diaria × noites` |
| status | texto | `pendente` → `confirmada` ou `cancelada` |

### Pagamento (`pagamentos.db`)
| Campo | Tipo | Regras |
|---|---|---|
| id | inteiro | chave primária |
| id_reserva | inteiro | ID do serviço de reservas |
| valor | decimal | maior que zero e igual ao `valor_total` da reserva |
| forma_pagamento | texto | `pix`, `cartao` ou `dinheiro` |
| data_pagamento | data/hora (UTC) | preenchida automaticamente |
| status | texto | `aprovado` |

## 4. Endpoints

Todos os serviços têm `GET /api/health`, que responde `{"status": "no ar", "servico": "<nome>"}`.

### Hóspedes — porta 5001
| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| POST | `/api/hospedes` | Cadastra hóspede | 201, 400 |
| GET | `/api/hospedes` | Lista hóspedes | 200 |
| GET | `/api/hospedes/<id>` | Busca hóspede (usado pela integração 1) | 200, 404 |
| PUT | `/api/hospedes/<id>` | Atualiza campos enviados | 200, 400, 404 |
| DELETE | `/api/hospedes/<id>` | Exclui hóspede | 200, 404 |

### Quartos — porta 5002
| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| POST | `/api/quartos` | Cadastra quarto | 201, 400 |
| GET | `/api/quartos` | Lista quartos (ordenados pelo número) | 200 |
| GET | `/api/quartos/<id>` | Busca quarto | 200, 404 |
| GET | `/api/quartos/<id>/disponibilidade` | Situação do quarto e valor da diária (usado pela integração 2) | 200, 404 |
| PUT | `/api/quartos/<id>` | Atualiza campos enviados | 200, 400, 404 |
| DELETE | `/api/quartos/<id>` | Exclui quarto | 200, 404 |

### Reservas — porta 5003
| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| POST | `/api/reservas` | Cria reserva (chama hóspedes e quartos) | 201, 400, 404, 502, 503 |
| GET | `/api/reservas` | Lista reservas | 200 |
| GET | `/api/reservas/<id>` | Busca reserva | 200, 404 |
| PUT | `/api/reservas/<id>/status` | Altera status; aceita `valor_pago` opcional (usado pela integração 3) | 200, 400, 404, 409 |
| DELETE | `/api/reservas/<id>` | Exclui reserva | 200, 404 |

### Pagamentos — porta 5004
| Método | Rota | Descrição | Respostas |
|---|---|---|---|
| POST | `/api/pagamentos` | Registra pagamento e confirma a reserva | 201, 400, 404, 409, 502, 503 |
| GET | `/api/pagamentos` | Lista pagamentos | 200 |
| GET | `/api/pagamentos/<id>` | Busca pagamento | 200, 404 |
| DELETE | `/api/pagamentos/<id>` | Exclui pagamento | 200, 404 |

## 5. Fluxos de integração

### 5.1 Criar reserva (integrações 1 e 2)
1. Valida `hospede_id`, `quarto_id` e as datas (formato e saída depois da entrada).
2. **GET** no serviço de hóspedes. Se a resposta for 404, retorna "Hóspede não encontrado".
3. **GET** na disponibilidade do quarto. Se a resposta for 404, retorna "Quarto não encontrado"; se o quarto estiver `indisponivel`, retorna 400.
4. Procura no próprio banco reservas não canceladas do mesmo quarto com datas sobrepostas (`entrada_existente < nova_saida` e `saida_existente > nova_entrada`).
5. Calcula `valor_total = valor_diaria × noites` e grava a reserva com status `pendente`.

### 5.2 Registrar pagamento (integração 3, com compensação)
1. Valida `id_reserva`, `valor` (maior que zero) e `forma_pagamento`.
2. Recusa o pagamento (409) se já existir um pagamento aprovado para a mesma reserva.
3. Grava o pagamento com status `aprovado`.
4. Envia **PUT** `/api/reservas/<id>/status` com `{"status": "confirmada", "valor_pago": <valor>}`.
5. O serviço de reservas recusa a confirmação quando:
   - a reserva não existe (404);
   - a reserva está cancelada (400);
   - a reserva já está confirmada (409);
   - o `valor_pago` é diferente do `valor_total` (400).
6. **Compensação:** se o PUT não retornar 200, ou se o serviço de reservas estiver fora do ar, o pagamento gravado no passo 3 é **apagado** e o erro é devolvido ao cliente com a mensagem "O pagamento foi desfeito". Se até a remoção falhar, a API responde 500 e informa que é necessária correção manual.

## 6. Tratamento de erros

| Situação | Exceção | HTTP | Exemplo de resposta |
|---|---|---|---|
| Dado inválido ou regra de negócio violada | `RegraDeNegocioError` | 400 / 404 / 409 | `{"erro": "Já existe um quarto com este número."}` |
| Outro serviço não respondeu em 5 s | `ErroIntegracao` | 503 | `{"erro": "O serviço quartos não respondeu dentro de 5 segundos."}` |
| Outro serviço desligado | `ErroIntegracao` | 503 | `{"erro": "O serviço reservas está indisponível. Verifique se está iniciado."}` |
| Outro serviço respondeu erro inesperado | `ErroIntegracao` | 502 | `{"erro": "Não foi possível consultar ..."}` |

Todas as respostas de erro usam o formato `{"erro": "mensagem"}`. Cada requisição recebida e cada chamada entre serviços aparece no terminal (ex.: `[reservas] chamando GET http://127.0.0.1:5001/api/hospedes/1`), o que ajuda na demonstração.

## 7. Configuração

| Variável de ambiente | Padrão local | Uso |
|---|---|---|
| `HOSPEDES_URL` | `http://127.0.0.1:5001` | Endereço do serviço de hóspedes |
| `QUARTOS_URL` | `http://127.0.0.1:5002` | Endereço do serviço de quartos |
| `RESERVAS_URL` | `http://127.0.0.1:5003` | Endereço do serviço de reservas |
| `PAGAMENTOS_URL` | `http://127.0.0.1:5004` | Endereço do serviço de pagamentos |
| `PORT` | porta fixa de cada serviço | Definida automaticamente pelo Render |

O passo a passo de execução local e de publicação no Render está no `README.md`.

## 8. Limitações conhecidas

- **SQLite no Render gratuito:** os arquivos `.db` são apagados quando o serviço reinicia ou hiberna. Hóspedes e quartos de exemplo são recriados; reservas e pagamentos se perdem.
- **Consistência entre serviços:** se o PUT de confirmação for aplicado, mas a resposta não chegar dentro do tempo limite, o pagamento é desfeito enquanto a reserva fica confirmada. Esse é o caso que exige correção manual.
- **Disponibilidade do quarto:** a rota recebe as datas, mas informa só a situação administrativa do quarto. O conflito de datas é verificado pelo serviço de reservas, que tem o histórico.
- **Sem autenticação:** a API não tem login nem controle de acesso por perfil de usuário.
