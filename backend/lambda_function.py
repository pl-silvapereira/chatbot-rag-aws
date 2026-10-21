import json
import boto3

# Cliente AWS configurado explicitamente na região us-east-2
ssm_client = boto3.client('ssm', region_name='us-east-2')
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-2')

# Identificador do perfil de inferência regional para o Amazon Nova 2 Lite
MODEL_ARN = 'us.amazon.nova-2-lite-v1:0'

# Prompt customizado para forçar o idioma Português (ou Inglês sob demanda)
PROMPT_TEMPLATE = """Você é um assistente virtual especialista em análise de documentos privados via RAG.

Diretrizes de Idioma e Comportamento:
1. Responda SEMPRE em Português (Brasil) por padrão.
2. Caso o usuário solicite explicitamente a resposta em Inglês (ou faça a pergunta inteiramente em Inglês), responda em Inglês.
3. Seja claro, objetivo e cortês.
4. Utilize formatação Markdown (listas, negrito) para organizar as ideias.
5. Responda estritamente com base nos documentos de contexto fornecidos.

Informações dos Documentos:
$search_results$

Instruções de Formato:
$output_format_instructions$

Pergunta do Usuário: $query$"""

def obter_kb_id():
    """Lê o ID da Knowledge Base gravado no SSM Parameter Store (.env da AWS)"""
    response = ssm_client.get_parameter(Name='/chatbot/KNOWLEDGE_BASE_ID')
    return response['Parameter']['Value']

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        body = json.loads(event.get('body', '{}'))
        pergunta = body.get('pergunta')

        if not pergunta:
            return {
                'statusCode': 400, 
                'headers': headers, 
                'body': json.dumps({'erro': 'A pergunta não pode estar em branco.'})
            }

        kb_id = obter_kb_id()

        # Chamada ao RAG no Bedrock com a chave 'textPromptTemplate' corrigida
        response = bedrock_agent.retrieve_and_generate(
            input={'text': pergunta},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': MODEL_ARN,
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': PROMPT_TEMPLATE
                        }
                    }
                }
            }
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'resposta': response['output']['text']})
        }

    except Exception as e:
        print(f"Erro detalhado na Lambda: {str(e)}")
        return {
            'statusCode': 500, 
            'headers': headers, 
            'body': json.dumps({'erro': f"Erro interno: {str(e)}"})
        }