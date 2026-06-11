# Documentação de uso do Bruno para a API do projeto

## 1. O que é o Bruno

O Bruno é um cliente de API local-first e Git-native. Ele trabalha com coleções salvas como arquivos no disco, o que facilita versionamento, revisão e compartilhamento via repositório. No site oficial você baixa a versão para Windows e acessa a documentação geral em https://www.usebruno.com/ e https://docs.usebruno.com/.

Neste repositório, a API backend expõe suas rotas com prefixo /api, conforme definido em apps/backend/main.py, e a porta padrão do backend é 8000, conforme apps/backend/config.py. Por isso, em ambiente local, a base mais comum é http://127.0.0.1:8000/api.

## 2. Instalação do Bruno no Windows

* Acesse o site oficial do Bruno e baixe o instalador para Windows.

* Execute o instalador e conclua a instalação normalmente.

* Abra o Bruno pela área de trabalho ou pelo menu Iniciar.

* Se necessário, reinicie o aplicativo após a instalação para garantir que a interface carregue corretamente.

## 3. Como abrir a collection deste projeto

O diretório de testes da API está em apps/backend/bruno/backend/. Você tem duas formas práticas de usar isso no Bruno.

A primeira, e geralmente a melhor, é abrir essa pasta como workspace/collection no Bruno. Isso mantém tudo organizado e próximo do código-fonte.

A segunda é importar os arquivos prontos do repositório. Os arquivos já preparados para isso são:

```
apps/backend/bruno/backend/collection.postman.json
apps/backend/bruno/backend/environment.example.postman.json
```

Se já houver um arquivo de ambiente ativo, ele está em apps/backend/bruno/backend/environment.postman.json.

Passo a passo recomendado:

* No Bruno, escolha a opção de abrir coleção/pasta.

* Aponte para apps/backend/bruno/backend/.

* Se preferir importar, selecione a collection JSON.

* Importe também o environment example.

* Depois selecione o environment ativo dentro do Bruno.

## 4. Como preencher o environment example

O environment de exemplo já vem com a base correta para execução local. Os campos são estes:

* API_BASE_URL: http://127.0.0.1:8000/api

* consulta_id: deixe vazio até criar uma consulta

* upload_id: deixe vazio até iniciar um upload

* token: deixe vazio até obter um token válido de cliente

Esse conjunto aparece tanto no arquivo de exemplo quanto no environment pronto do repositório.

A diferença prática é que o example serve como modelo, enquanto o environment ativo é o que você usa no dia a dia.

### Regra principal:

* Se o backend estiver em outro host ou porta, ajuste API_BASE_URL.

* Se o backend estiver com a configuração padrão deste projeto, use http://127.0.0.1:8000/api.

## 5. Ordem recomendada de uso da collection

A collection foi organizada por fluxo de teste da API, e a sequência mais útil costuma ser esta:

1. Health
- Faz uma chamada GET em /health.
- Serve para confirmar que o backend está no ar.

2. Config
- GET /config para ler a configuração atual.
- PUT /config para atualizar parâmetros do modelo.
- O corpo do PUT já vem com valores de exemplo.

3. Consultas
- GET /consultas lista as consultas existentes.
- POST /consultas cria uma nova consulta com upload de base.
- GET /consultas/{consulta_id} mostra os detalhes.
- GET /consultas/{consulta_id}/clusters traz os clusters.
- GET /consultas/{consulta_id}/clientes traz os clientes paginados.
- GET /consultas/{consulta_id}/clientes/export baixa o CSV.

4. Uploads
- POST /uploads/iniciar inicia um upload e retorna upload_id.
- POST /uploads/{upload_id}/chunk envia um chunk.
- POST /uploads/{upload_id}/finalizar conclui o upload e retorna uma consulta.

5. Clientes
- GET /clientes/{token} consulta o histórico de um cliente.

## 6. Como executar cada fluxo

Health:
- Rode a chamada Health primeiro.
- Se a resposta vier correta, o backend está acessível.

Config:
- Use GET /config para inspecionar os parâmetros.
- Use PUT /config quando quiser alterar t, LGD, u_bar, L_max e T.
- O request já está preparado com Content-Type application/json e um corpo de exemplo.

Consultas:
- Para criar consulta com arquivo, use o request de upload de arquivo.
- O endpoint espera um arquivo .parquet.
- Depois da criação, salve o retorno que contém o consulta_id.
- Use esse valor nas chamadas de detalhe, clusters, clientes e exportação.

Uploads:
- Inicie com /uploads/iniciar.
- Guarde o upload_id retornado.
- Envie os chunks na ordem correta.
- Finalize com /uploads/{upload_id}/finalizar.
- O retorno final contém a consulta criada; salve o id em consulta_id.

Clientes:
- Preencha token com o valor do cliente que você quer consultar.
- Rode /clientes/{token} para ver o histórico.

## 7. Observações importantes

- O backend roda sob o prefixo /api, então a base correta no Bruno não é só http://127.0.0.1:8000, e sim http://127.0.0.1:8000/api.

- A collection foi pensada para testes manuais e também para validação do fluxo do backend.

- O arquivo environment.example.postman.json deve ser tratado como template; o ideal é duplicar ou importar e então manter um environment local para uso diário.

- Se você importar a collection no Bruno, os valores vazios de consulta_id, upload_id e token devem ser preenchidos dinamicamente conforme você executar os requests.

## 8. Resumo prático

Se você quiser testar rápido:

1. Abra o backend.
2. Abra o Bruno.
3. Importe a collection e o environment.
4. Confirme API_BASE_URL como http://127.0.0.1:8000/api.
5. Execute Health.
6. Execute Config ou Consultas conforme o teste desejado.
7. Preencha consulta_id, upload_id e token com os valores retornados pelas próprias rotas.