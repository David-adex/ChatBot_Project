# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 13:58:16 2023

@author: david
"""
#import azure agents
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
#######################################################
import time
import os
import json, requests, uuid
#######################################################
#  Initialise AUDIO agent
import pyaudio
import wave

class azure_partD():        
        def getDisplay_Text(self,image):
            cog_key = '11722dd640874badafaecb684c85c23a' 
            cog_endpoint = 'https://partd.cognitiveservices.azure.com/'

            # Read the image file
            image_path = os.path.join('image_data', image)
            image_stream = open(image_path, "rb")

            # Get a client for the computer vision service
            computervision_client = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

            # Submit a request to read printed text in the image and get the operation ID
            read_operation = computervision_client.read_in_stream(image_stream,raw=True)
            operation_location = read_operation.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            # Wait for the asynchronous operation to complete
            while True:
                read_results = computervision_client.get_read_result(operation_id)
                if read_results.status not in [OperationStatusCodes.running]:
                    break
                time.sleep(1)

            # If the operation was successfuly, process the text line by line
            if read_results.status == OperationStatusCodes.succeeded:
                for result in read_results.analyze_result.read_results:
                    for line in result.lines:
                        print(line.text)
        def change_language(self,image,lan_code,from_lang='en'):
            global x
            cog_key = '11722dd640874badafaecb684c85c23a'
            cog_endpoint = 'https://partd.cognitiveservices.azure.com/'
            cog_region = 'uksouth'
            image_path = os.path.join('image_data', image)
            image_stream = open(image_path, "rb")

            # Get a client for the computer vision service
            computervision_client = ComputerVisionClient(cog_endpoint, CognitiveServicesCredentials(cog_key))

            # Submit a request to read printed text in the image and get the operation ID
            read_operation = computervision_client.read_in_stream(image_stream,raw=True)
            operation_location = read_operation.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            # Wait for the asynchronous operation to complete
            while True:
                read_results = computervision_client.get_read_result(operation_id)
                if read_results.status not in [OperationStatusCodes.running]:
                    break
                time.sleep(1)

            # If the operation was successfuly, process the text line by line
            image_text =''
            if read_results.status == OperationStatusCodes.succeeded:
                for result in read_results.analyze_result.read_results:
                    for line in result.lines:
                        image_text += " "+line.text
            path = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
            params = '&from={}&to={}'.format(from_lang, lan_code)
            constructed_url = path + params

            # Prepare the request headers with Cognitive Services resource key and region
            headers = {
                'Ocp-Apim-Subscription-Key': cog_key,
                'Ocp-Apim-Subscription-Region':cog_region,
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
                }

            # Add the text to be translated to the body
            body = [{
                'text': image_text }]

            # Get the translation
            request = requests.post(constructed_url, headers=headers, json=body)
            response = request.json()
            x= response[0]["translations"][0]["text"]
            if x:
                print(x)
            else:
                print("Cannot change text to specified language")
        def voice_output(self,lan2):
            cog_key = '11722dd640874badafaecb684c85c23a'
            cog_region = 'uksouth'
            speech_config = SpeechConfig(cog_key, cog_region)
            speech_config.speech_synthesis_language = lan2
            output_file = os.path.join('voice_data', 'response.wav')
            audio_output = AudioConfig(filename=output_file)
            speech_synthesizer = SpeechSynthesizer(speech_config, audio_output)

            # Transcribe text into speech
            speech_synthesizer.speak_text(x)
            audio_file = wave.open(output_file, 'rb')

            # Create an instance of the PyAudio class
            p = pyaudio.PyAudio()

            # Open a stream to play the audio file
            stream = p.open(format=p.get_format_from_width(audio_file.getsampwidth()), 
                            channels=audio_file.getnchannels(),
                            rate=audio_file.getframerate(),
                            output=True)

            # Read and play chunks of the audio file
            chunk_size = 1024
            data = audio_file.readframes(chunk_size)
            while data:
                stream.write(data)
                data = audio_file.readframes(chunk_size)

            # Close the stream and PyAudio instance
            stream.stop_stream()
            stream.close()
            p.terminate()