import flask
import magic
import json
from flask import request, jsonify, send_from_directory, Response
from flask_cors import CORS, cross_origin
from audio import Audio, audio_psnr
from requests_toolbelt import MultipartEncoder

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/', methods=['GET'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def home():
    return "Hello World!"

@app.route('/audio/embedding', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def audio_embedding_api():
    if request.method == "POST":
        print("Reading data")
        data = request.form.to_dict()
        files = request.files.to_dict()
        
        # Proesss
        audio = Audio(data, files, mode='embedding')
        # audio.embedding()
        # print("Counting PSNR")
        # psnr = audio_psnr(audio.container_file_path, audio.encrypted_file_path)
        psnr = 69

        # Response
        print("Building Response")
        mime = magic.Magic(mime=True)
        # m = MultipartEncoder(
        #     fields={
        #         'psnr': str(psnr),
        #         'encryptedFileName': audio.encrypted_file_name,
        #         'encryptedFileType': mime.from_file(audio.encrypted_file_path),
        #         'encryptedFile': (audio.encrypted_file_path, open(audio.encrypted_file_path, 'rb'), mime.from_file(audio.encrypted_file_path))
        #     }
        # )
        open_file = open(audio.encrypted_file_path, 'rb')
        bytes_json = open_file.read()
        open_file.close()
        # bytes_array_json = bytearray(bytes_json)
        # bytes_int = [int(byte) for byte in bytes_array_json]
        response_json = jsonify({
            'psnr': str(psnr),
            'encryptedFileName': audio.encrypted_file_name,
            'encryptedFileType': mime.from_file(audio.encrypted_file_path),
            'encryptedFile': str(bytes_json)
        })
        return response_json, 200
    else:
        return jsonify({'message': "Input file not appropriate"}), 400

@app.route('/audio/extract', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def audio_extract_api():
    if request.method == "POST":
        print("Reading data")
        data = request.form.to_dict()
        files = request.files.to_dict()
        
        # Process
        audio = Audio(data, files, mode='extract')
        audio.extract()

        # Response
        print("Building Response")
        mime = magic.Magic(mime=True)
        m = MultipartEncoder(
            fields={
                'messageFileName': audio.output_file_name,
                'messageFileType': mime.from_file(audio.output_file_path),
                'messageFile': (audio.output_file_name, open(audio.output_file_path, 'rb'), mime.from_file(audio.output_file_path)),
                'containerFileName': audio.container_file_name,
                'containerFilePath': audio.container_file_path,
                'containerFile': (audio.container_file_name, open(audio.container_file_path, 'rb'), mime.from_file(audio.container_file_path))
            }
        )
        return (m.to_string(), {'Content-Type': m.content_type})

    else:
        return jsonify({'message': "Input file not appropriate"}), 400

app.run()