# Sistema de Gerenciamento de Hotel

## Documento de requisitos

### Propósito do sistema
Desenvolver uma aplicação back-end para organizar as principais operações de um hotel, permitindo controlar hóspedes, quartos, reservas e pagamentos por meio de quatro microsserviços independentes.

### Usuários
- Administradores do hotel: gerenciam os cadastros e acompanham a operação.
- Recepcionistas: cadastram hóspedes, consultam quartos e realizam reservas.
- Funcionários do financeiro: registram e consultam pagamentos.

### Requisitos funcionais
1. O sistema deve permitir cadastrar, listar, consultar, atualizar e excluir hóspedes.
2. O sistema deve permitir cadastrar, listar, consultar, atualizar e excluir quartos.
3. O sistema deve permitir consultar a situação de disponibilidade de um quarto.
4. O sistema deve permitir criar, listar, consultar, atualizar o status e excluir reservas.
5. O sistema deve validar a existência do hóspede antes de criar uma reserva.
6. O sistema deve validar a existência e a situação disponível do quarto antes de criar uma reserva.
7. O sistema deve impedir reservas com datas inválidas ou períodos sobrepostos para o mesmo quarto.
8. O sistema deve calcular o valor total da reserva com base no valor da diária e na quantidade de noites.
9. O sistema deve permitir registrar e consultar pagamentos vinculados a uma reserva.
10. O sistema deve registrar o pagamento aprovado e solicitar a confirmação da reserva por meio de uma chamada PUT.
11. Se a atualização da reserva falhar, o serviço de pagamentos deve desfazer o pagamento local ou informar claramente que é necessária correção manual.
12. O valor do pagamento deve ser igual ao valor total da reserva; caso contrário, o pagamento é recusado e desfeito.
13. Cada reserva aceita apenas um pagamento aprovado; reservas já confirmadas ou canceladas não podem ser pagas.

## Descritivo técnico

| Microsserviço | Porta local | Banco SQLite | Responsabilidade |
|---|---:|---|---|
| `servico_hospedes` | 5001 | `hospedes.db` | Dados pessoais dos hóspedes. |
| `servico_quartos` | 5002 | `quartos.db` | Número, tipo, capacidade, valor da diária e situação dos quartos. |
| `servico_reservas` | 5003 | `reservas.db` | IDs de hóspede e quarto, datas, valor total e situação da reserva. |
| `servico_pagamento` | 5004 | `pagamentos.db` | ID da reserva, valor, forma, data e situação do pagamento. |

Cada serviço possui seu próprio banco. Os IDs que apontam para outros serviços são armazenados como números comuns, sem `ForeignKey` entre bancos.

## Integrações entre microsserviços

| # | Tipo | Quem chama | Quem responde | Rota | Função |
|---|---|---|---|---|---|
| 1 | GET | Reservas | Hóspedes | `GET /api/hospedes/<id>` | Busca os dados do hóspede antes de criar a reserva. |
| 2 | GET | Reservas | Quartos | `GET /api/quartos/<id>/disponibilidade?data_entrada=AAAA-MM-DD&data_saida=AAAA-MM-DD` | Verifica se o quarto existe e está marcado como disponível para o período informado. O serviço de reservas também verifica conflitos de datas no próprio banco. |
| 3 | PUT | Pagamentos | Reservas | `PUT /api/reservas/<id>/status` | Envia `{"status": "confirmada", "valor_pago": <valor>}`. O serviço de reservas confere se o valor é igual ao total e se a reserva ainda não foi confirmada ou cancelada. Se a reserva recusar ou o serviço falhar, o pagamento local é removido como compensação. |

As chamadas usam `requests`, timeout de 5 segundos e variáveis de ambiente. Em desenvolvimento local, os endereços padrão são `127.0.0.1` nas portas indicadas. Na publicação, configure as URLs públicas do Render.

## Estrutura

Cada microsserviço contém `app.py`, `models.py`, `regras.py`, `rotas.py`, `integracao.py` e `erros.py`. Os testes da extensão REST Client ficam na pasta `rest-client/`.

## Como executar no Windows

1. Abra um terminal nesta pasta (`modelo-projeto-flask`).
2. Crie e ative o ambiente virtual:
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
4. Inicie os quatro serviços:
   ```powershell
   .\iniciar_servicos.bat
   ```
   Ou abra quatro terminais e execute `py app.py` dentro de cada pasta de serviço.
5. Confirme que os serviços estão no ar usando `GET /api/health` nos arquivos `.http`.
6. Abra os arquivos de `rest-client/` no VS Code com a extensão REST Client instalada e clique em **Send Request**.

## Ordem sugerida de demonstração

1. Inicie os quatro serviços.
2. Execute `hospedes.http` e confirme que existe o hóspede de exemplo com ID 1.
3. Execute `quartos.http` e confirme que existe o quarto de exemplo com ID 1.
4. Execute a criação de reserva em `reservas.http`. O serviço de reservas fará as duas chamadas GET.
5. Confira o valor total calculado. Com o quarto 1 de exemplo (R$ 150,00 por diária) e três noites, o total será R$ 450,00.
6. Use esse valor no POST de `pagamento.http`. O serviço de pagamentos enviará o PUT para confirmar a reserva; se a reserva não existir, o valor for diferente do total ou a atualização falhar, o pagamento será desfeito.
7. Consulte a reserva novamente para verificar o status `confirmada`.

## Observações

- Os dados iniciais de hóspedes e quartos são criados quando os respectivos bancos estão vazios. Reservas e pagamentos não recebem dados iniciais porque dependem de IDs reais de outros serviços.
- O campo `valor` foi incluído em pagamentos porque é necessário registrar quanto foi pago. Ele é enviado no PUT de confirmação como `valor_pago`, e o serviço de reservas o compara com o `valor_total`.
- Os arquivos `.db` não precisam ser criados manualmente: cada serviço cria o seu banco SQLite (`db.create_all()`) na primeira vez que é iniciado.
- O documento técnico completo está em `DOCUMENTO-TECNICO.md`.
- A disponibilidade do quarto representa a situação administrativa (`disponivel` ou `indisponivel`). A verificação de choque entre datas de reservas é feita pelo próprio microsserviço de reservas, que possui o histórico de reservas.
- Em produção, o plano gratuito do Render pode apagar arquivos SQLite em reinicializações. Os dados de exemplo de hóspedes e quartos são recriados na inicialização.

## Publicação no Render

Cada microsserviço é publicado como um **Web Service** separado no Render, todos a partir do mesmo repositório do GitHub.

### 1. Configuração de cada serviço

| Campo no Render | `servico_hospedes` | `servico_quartos` | `servico_reservas` | `servico_pagamento` |
|---|---|---|---|---|
| Root Directory | `Sistema-Gerenciamento-Hotel-corrigido/modelo-projeto-flask/servico_hospedes` | `.../servico_quartos` | `.../servico_reservas` | `.../servico_pagamento` |
| Runtime | Python 3 | Python 3 | Python 3 | Python 3 |
| Build Command | `pip install -r requirements.txt` | igual | igual | igual |
| Start Command | `gunicorn app:app` | igual | igual | igual |

O Root Directory deve apontar para a pasta do serviço, porque o Render só enxerga essa pasta. Por isso cada serviço tem o próprio `requirements.txt`, já com o `gunicorn`. A porta é definida automaticamente pelo Render.

### 2. Variáveis de ambiente (aba *Environment*)

Depois que os quatro serviços estiverem criados, copie a URL pública de cada um (ex.: `https://servico-hospedes-xxxx.onrender.com`, sem barra no final) e cadastre:

| Serviço no Render | Variáveis obrigatórias |
|---|---|
| `servico_reservas` | `HOSPEDES_URL` e `QUARTOS_URL` |
| `servico_pagamento` | `RESERVAS_URL` |
| `servico_hospedes` e `servico_quartos` | nenhuma (não chamam outros serviços) |

Se preferir, cadastre as quatro variáveis (`HOSPEDES_URL`, `QUARTOS_URL`, `RESERVAS_URL`, `PAGAMENTOS_URL`) em todos os serviços ou em um *Environment Group* compartilhado. Sem essas variáveis, o código usa `127.0.0.1` e as integrações falham online.

### 3. Testar online

1. Abra `https://<url-do-servico>/api/health` de cada serviço. No plano gratuito, o primeiro acesso pode levar até 1 minuto, porque o serviço "acorda".
2. Nos arquivos de `rest-client/`, troque o `@baseUrl` pela URL do Render correspondente e repita a ordem de demonstração.
3. Antes de criar a reserva, acorde os quatro serviços pelo `/api/health`, para evitar que uma integração estoure o tempo limite de 5 segundos.
