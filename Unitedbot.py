#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import class from another file
from partD_services import azure_partD
#class is defined
partD=azure_partD()
#Initialise fuzzy logic agent 
from fuzzywuzzy import fuzz
#######################################################
#  Initialise NLTK Inference
#######################################################
from nltk.sem import Expression
from nltk.inference import ResolutionProver
read_expr = Expression.fromstring
#######################################################
# Initialise CSV simlarity agents
#######################################################
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#######################################################
#  Initialise Knowledgebase.
kb=[]
data = pd.read_csv('kb.csv', header=None)
[kb.append(read_expr(row)) for row in data[0]]
#######################################################
#  Initialise AIML agent
#######################################################
import aiml
import pyttsx3
# Create a Kernel object. No string encoding (all I/O is unicode)
kern = aiml.Kernel()
kern.setTextEncoding(None)
# Use the Kernel's bootstrap() method to initialize the Kernel. The
# optional learnFiles argument is a file (or list of files) to load.
# The optional commands argument is a command (or list of commands)
# to run after the files are loaded.
# The optional brainFile argument specifies a brain file to load.
kern.bootstrap(learnFiles="mybot-basic.xml")
df = pd.read_csv('ManchesterUnitedQA.csv', header=None)
#######################################################
# Welcome user
#######################################################
print("\nWelcome to this Manchester United Informant chat bot. \nPlease feel free to ask questions from me!")
#######################################################
# Main loop
###############################################u########
while True:            
    global response
    #get user input
    try:
        userInput = input("> ")
    except (KeyboardInterrupt, EOFError):
        print("Bye!")
        break
    #pre-process user input and determine response agent (if needed)
    responseAgent = 'aiml'
    #activate selected response agent
    if responseAgent == 'aiml':
        answer = kern.respond(userInput)
        image_name = kern.getPredicate("image")
        lan1=kern.getPredicate("lan")
    #post-process the answer for commands
    if answer.startswith('#'):
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            print(params[1])
            break
        #get image text
        elif cmd == 33:
            image_name1=image_name+".jpg"
            partD.getDisplay_Text(image_name1)
        # change image text to another language
        elif cmd == 21:
            object, subject = params[1].split(' in ')
            image_name2= object+".jpg"
            #defined other langiage codes that were unique
            if subject=='turkish':
                code='tr'
            elif subject=='spanish':
                code='es'
            elif subject=='german':
                code='de'
            elif subject=='portuguese':
                code='pt'
            elif subject=='swedish':
                code='sv'
            else:
                code = subject[:2]
            partD.change_language(image_name2, code, from_lang='en')
        #say translated text function
        elif cmd == 22:
            #defined other langiage codes that were unique
            if lan1=='turkish':
                code='tr'
            elif lan1=='spanish':
                code='es'
            elif lan1=='german':
                code='de'
            elif lan1=='portuguese':
                code='pt'
            elif lan1=='swedish':
                code='sv'
            else:
                code = subject[:2]
            partD.voice_output(code)
        #display answers to peculiar questions
        elif cmd == 1:
            Vector_maker = TfidfVectorizer()
            tf_idf= Vector_maker.fit_transform(df[0])
            Userinput_Vector =Vector_maker.transform([userInput])
            vectors_Similarity= cosine_similarity(Userinput_Vector, tf_idf)
            most_similar=vectors_Similarity.argmax()
                        
            response = df.loc[most_similar, 1]
            print(response)
        #say the answers function
        elif cmd==2:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)
            engine.say(response)
            engine.runAndWait()
        # if input pattern is "I know that * is *"
        elif cmd == 31:
             object, subject = params[1].split(' is ')
             options = ["Winger", "Defender", "CDM", "GoalKeeper", "Midfielder", "Striker", "Popular", "Good", "Rich"]
             search_term = subject
             best_match = max(options, key=lambda x: fuzz.ratio(search_term.lower(), x.lower()))
             if subject.islower():
                 subject=best_match
             if best_match:
                 expr=read_expr(subject + '(' + object + ')')
                 contradicts=ResolutionProver().prove(expr, kb, verbose=True)
                 if contradicts:
                     kb.append(expr) 
                     print('OK, I will remember that',object,'is', subject)
                 if not contradicts:
                     print("Sorry this contradicts what I know")
                 
        elif cmd == 32: # if the input pattern is "check that * is *"
             object, subject = params[1].split(' is ')
             expr=read_expr(subject + '(' + object + ')')
             answer=ResolutionProver().prove(expr, kb, verbose=True)
             if answer:
                print('Correct')                
             elif not answer and subject=="Winger" or subject== "Defender"or subject=="CDM"or subject=="GoalKeeper"or subject=="Midfielder" or subject== "Striker"or subject== "Popular"or subject== "Good"or subject=="Rich":
                print('Incorrect')
             else:
                print('Sorry I do not know')
        elif cmd == 99:
            print("I did not get that, please try again.")
    else:
        print(answer)