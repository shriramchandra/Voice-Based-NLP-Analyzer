#!/usr/bin/env python3
#Inspired from https://github.com/shriramchandra/speech_recognition
import speech_recognition as sr
import os;
import sys,getopt;
import os.path;
import time;
import pyaudio;
import wave;
import subprocess;
import re;
import webbrowser;
import nltk;
from gtts import gTTS;
from tempfile import TemporaryFile;
from textblob import TextBlob;

# obtain audio from the microphone
#m = sr.Microphone()

def GetGoogleTranscripts( r,sr,audio ):
    # recognize speech using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        googleTranscript=r.recognize_google(audio);
        return str(googleTranscript);
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def GetIBMWatsonTranscripts( r,sr,audio ):
    # recognize speech using IBM Speech to Text
    IBM_USERNAME = "" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    IBM_PASSWORD = "" # IBM Speech to Text passwords are mixed-case alphanumeric strings
    try:
        ibmTranscript=r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD);
        return str(ibmTranscript);
    except sr.UnknownValueError:
        print("IBM Speech to Text could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from IBM Speech to Text service; {0}".format(e))

    
def GetSqlCommands( transcript ):
    sql_gen.ExecuteSqlCommand(transcript)

def Text2SpeechRequest (fileName,inpText):
    extensionMp3=".mp3"
    extensionWav=".wav"
    fullMp3FilePathName="C:\\texttospeech\\"+fileName+extensionMp3
    fullWavFilePathName="C:\\texttospeech\\"+fileName+extensionWav
    if os.path.isfile(fullWavFilePathName) :
        PlaySound(fullWavFilePathName);
    else:
        tts = gTTS(text=inpText, lang='en-us');
        tts.save(fullMp3FilePathName);
        f = TemporaryFile();
        tts.write_to_fp(f);
        f.close();
        subprocess.call(['C:\\Temp\\ffmpeg\\bin\\ffmpeg', '-i', fullMp3FilePathName,fullWavFilePathName])
        PlaySound(fullWavFilePathName);
    return;
    
def PlaySound (wavFile) :
    chunk = 1024
    try:
        wf = wave.open(wavFile, 'rb')
    except IOError as ioe:
        sys.stderr.write('IOError on file ' + wav_filename + '\n' + \
        str(ioe) + '. Skipping.\n')
        return
    except EOFError as eofe:
        sys.stderr.write('EOFError on file ' + wav_filename + '\n' + \
        str(eofe) + '. Skipping.\n')
        return
    # Instantiate PyAudio.
    p = pyaudio.PyAudio()

    stream = p.open(
        format = p.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)
    data = wf.readframes(chunk)

    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(chunk)
# Stop stream.
    stream.stop_stream()
    stream.close()

    p.terminate()
    return;

def main(argv):

    #with sr.Microphone() as source:
    finalTranscript="";
    translationSuccess=0;
    optionChoosen ="0";
    exitOption="0"
    welcomeTextSpeak=0
    threeOptionAware=0
    while exitOption in ("0"):
        m = sr.Microphone();
        optionChoosen ="0";
        while optionChoosen not in ("1", "2", "3"):
            if welcomeTextSpeak == 0:
                welcomeTextSpeak = welcomeTextSpeak+1;
                welcomeText="Hello user. Welcome to Shriram's Voice based Natural Language Processing Tool"
                print(welcomeText)
                Text2SpeechRequest("for_welcome",welcomeText);
            
            silenceText="Please wait while I analyze your environment and self adjust myself to better undersand what you say"
            print(silenceText)
            Text2SpeechRequest("for_silence",silenceText);
            r = sr.Recognizer()
            with m as source: r.adjust_for_ambient_noise(source)
            thresholdText="Optimal Energy Threshold set to: {}".format(r.energy_threshold)
            print (thresholdText);
            
            if(r.energy_threshold > 500):
                environmentNoisyText="Your environment is noisy so please help me by speaking a bit loud"
                print(environmentNoisyText);
                Text2SpeechRequest("for_notifying_noisy_environment",environmentNoisyText);

                
            with sr.Microphone( device_index = None, sample_rate = 48000 ) as source:
                #----------------------------------------------------------------ASSISTING FOR OTHER OPTIONS--------------------------------------------------#   
                sayCommandText="Can you please say your request now"
                print(sayCommandText)
                Text2SpeechRequest("for_requesting_command",sayCommandText);
                
                audio = r.listen(source)

                waitForUnderstandingText="Please wait while I try to understand what you just said"
                print(waitForUnderstandingText)
                Text2SpeechRequest("for_waiting_to_undersanding_input",waitForUnderstandingText)
                if threeOptionAware==0:
                    threeOptionAware=threeOptionAware+1;
                    learningRequestText= "I am learning to understand how you speak, so I am going to provide you with two different options that represents what I understood.";
                    print(learningRequestText);
                    Text2SpeechRequest("for_notifying_about_2_options",learningRequestText);
                
                transcriptGoogle= GetGoogleTranscripts(r,sr,audio);
                if not transcriptGoogle =='None':
                    print("Option # 1: Did you spoke the following words? : " + transcriptGoogle)
                else:
                    print("Sorry I cannot recognize what you said. Please try again");
                    finalTranscript="";

                transcriptIbm= GetIBMWatsonTranscripts(r,sr,audio);
                if not transcriptIbm == 'None':
                    print("Option # 2: Did you spoke the following words? : " + transcriptIbm);
                else:
                    print("Sorry I cannot recognize what you said. Please try again")
                    finalTranscript="";
                
                choiceText='Please say the option number which closely relates to what you just said. If you are not satisfied please say restart.'
                print(choiceText)
                Text2SpeechRequest("for_getting_transcript_choice",choiceText);
                
                audioListenTranscriptChoice = r.listen(source)
                transcriptGoogleListenTranscriptChoice= GetGoogleTranscripts(r,sr,audioListenTranscriptChoice);
                
                if re.search( "1" , transcriptGoogleListenTranscriptChoice.lower()):
                    optionChoosen="1"
                    finalTranscript=transcriptGoogle;
                elif re.search( "2" , transcriptGoogleListenTranscriptChoice.lower()):
                    optionChoosen="2";
                    finalTranscript=transcriptIbm;
                else:
                    print("Restarting to get your request again and understand your request thoroughly");
                    optionChoosen="0"
                
                if optionChoosen in ("1", "2"):
                    if len(finalTranscript) > 0:
                        nltkOpsText= "Lets perform some natural language analysis on the text you had just talked ";
                        print(nltkOpsText)
                        Text2SpeechRequest("for_notifying_nltk_operations",nltkOpsText);
                        print("Parts Of Speech Tags in your sentence are :")
                        print(str(nltk.pos_tag(nltk.word_tokenize(finalTranscript))))
                        blob = TextBlob(finalTranscript);
                        print("Grammatical structure of your sentence is :");
                        print(blob.parse())
                        overAllSentiment = 0;
                        for sentence in blob.sentences:
                            overAllSentiment=overAllSentiment+sentence.sentiment.polarity;
                        print("Sentiment score of your sentence is :");
                        print(overAllSentiment)
                        if overAllSentiment > 0.0:
                            positiveText="You have spoken a positive sentence. Seems you are happy !";
                            print(positiveText);
                            Text2SpeechRequest("for_notifying_positive_sentiment",positiveText);
                        elif overAllSentiment < 0.0:
                            negativeText="You have spoken a negative sentence. Seems you are not happy.";
                            print(negativeText);
                            Text2SpeechRequest("for_notifying_negative_sentiment",negativeText);
                        else:
                            neutralText="You have spoken a neutral sentence.";
                            print(neutralText);
                            Text2SpeechRequest("for_notifying_neutral_text",neutralText);
                            
                        exitOptionText="Are you satisfied with the results that I had presented to you? Do you want me to help you with anything else?"
                        print(exitOptionText);
                        Text2SpeechRequest("for_exit_choice_getting",exitOptionText)
                        audioListenExit = r.listen(source)
                        transcriptGoogleListenExit= GetGoogleTranscripts(r,sr,audioListenExit);
                        if re.search( "yes|yeah|fine|yup|up|ok|satisfied" , transcriptGoogleListenExit.lower()):
                            exitOption="0";
                        elif re.search( "no|thats ok|i am good|done|thanks" , transcriptGoogleListenExit.lower()):
                            exitOption="1";
                else:
                    optionChoosen="0"
    sr.Microphone.MicrophoneStream.close;
    goodByeText="Thank you for using Shriram's NLP Application!. Hope I was of help to you. Have a great day"
    print(goodByeText)
    Text2SpeechRequest("for_goodbye_note",goodByeText)
        
if __name__ == '__main__':
    main(sys.argv[1:])
