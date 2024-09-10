from flask import Flask, request, jsonify
import json
import boto3
import logging
from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

session = boto3.Session()
bedrock = session.client(service_name='bedrock-runtime', region_name='ca-central-1')
bedrock_model_id = "meta.llama3-70b-instruct-v1:0"


@app.route('/process', methods=['POST'])
def process():
    try:
        form_data = request.get_json()
        usermessage = form_data.get('usermessage', '')

        prompt = f""" 
        <|begin_of_text|> 
        <|start_header_id|>user<|end_header_id|> 
        {usermessage} 
        <|eot_id|> 
        <|start_header_id|>assistant<|end_header_id|>
        """

        body = json.dumps({
            "prompt": prompt,
            "max_gen_len": 2048,
            "temperature": 0.5,
            "top_p": 0.9
        }).encode('utf-8')

        logger.info(f"Sending request to Bedrock with body: {body}")

        response = bedrock.invoke_model(body=body, modelId=bedrock_model_id, accept='application/json',
                                         contentType='application/json')
        response_body = json.loads(response.get('body').read())
        response_generation = response_body['generation']

        # 将 response_generation 以美化的 JSON 格式输出
        beautified_generation = json.dumps(response_generation, indent=4)

        return jsonify({"generation": beautified_generation}), 200, {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        }
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1233, ssl_context=('/mnt/scs1725630103671_sql2022.cn_server.crt', '/mnt/scs1725630103671_sql2022.cn_server.key'))