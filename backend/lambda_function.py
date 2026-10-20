import json
import boto3

ssm_client = boto3.client('ssm')
bedrock_agent = boto3.client('bedrock-agent-runtime')

# Modelo gerador (Claude 3 Sonnet)
MODEL_ARN = 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'

def obter_kb_id():
    """Lê a variável do SSM Parameter Store (Simulando o .env)"""
    response = ssm_client.get_parameter(Name='/chatbot/KNOWLEDGE_BASE_ID')
    return response['Parameter']['Value']

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        body = json.loads(event.get('body', '{}'))
        pergunta = body.get('pergunta')

        if not pergunta:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'erro': 'Pergunta em branco.'})}

        kb_id = obter_kb_id()

        # Chamada ao RAG no Bedrock
        response = bedrock_agent.retrieve_and_generate(
            input={'text': pergunta},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kb_id,
                    'modelArn': MODEL_ARN
                }
            }
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'resposta': response['output']['text']})
        }

    except Exception as e:
        print(f"Erro: {e}")
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'erro': 'Erro interno ao processar a pergunta.'})}