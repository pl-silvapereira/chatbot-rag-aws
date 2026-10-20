# 🧠 Chatbot RAG Serverless na AWS

Este repositório contém o código-fonte e as automações (CI/CD) para uma aplicação web de chatbot baseada em Inteligência Artificial. O sistema utiliza a arquitetura **RAG (Retrieval-Augmented Generation)** para responder a perguntas com base em documentos PDF específicos, operando em uma infraestrutura **100% Serverless** na AWS.

## 🎯 Objetivo

Criar uma solução didática, escalável e de baixo custo que demonstre como modelos fundacionais (LLMs) podem ser enriquecidos com conhecimento privado corporativo ou acadêmico sem a necessidade de re-treinamento, mitigando alucinações e garantindo rastreabilidade das informações.

## 🏗️ Arquitetura da Solução

O fluxo da aplicação é dividido em duas etapas principais: Ingestão de Dados e Inferência.

```mermaid
graph TD
    subgraph Frontend
        A[Usuário/Navegador] -->|Acessa via HTTPS| B(AWS Amplify)
    end
    
    subgraph API & Lógica
        A -->|Faz a pergunta| C(Amazon API Gateway)
        C -->|Aciona| D(AWS Lambda - Python)
    end
    
    subgraph Motor RAG & IA
        D -->|Consulta + Prompt| E(Amazon Bedrock Knowledge Bases)
        E -->|Gera Resposta| F(LLM - Claude 3 / Titan)
        E -->|Busca Semântica| G[(Amazon OpenSearch Serverless)]
    end
    
    subgraph Armazenamento
        H[Administrador] -->|Upload de PDFs| I(Amazon S3)
        I -->|Sincronização| E
    end