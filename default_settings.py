from gtts import gTTS
import os
import speech_recognition as sr
from playsound import playsound


class Settings(object):

    def __init__(self, microphone, recognizer, language):
        self.microphone = microphone
        self.recognition = recognizer
        self.language = language
        self.path_for_music = 'code directory here'

    def init_mic(self):
        """
        The method is used to calibrate the microphone before the interaction. User is informed
        by the computer about waiting time for calibration. At the end it plays 'beep' for showing
        that microphone is ready.
        :return:
        """
        print("Please wait, microphone is callibrating now. It will take 4 seconds.")
        print("You can speak after the beep sound.")
        with self.microphone as source:
            self.recognition.adjust_for_ambient_noise(source, duration=4)
        path = os.path.join(self.path_for_music, 'beep.mp3')
        playsound(path)

    def get_the_message(self):
        """
        The method is used in order to get the answers from the user.
        :return:
        """
        self.init_mic()
        speech_customer = ''
        with self.microphone as source:
            audio_customer = self.recognition.listen(source)
        try:
            speech_customer = self.recognition.recognize_google(audio_customer)
            return speech_customer
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand what you said!")
        except sr.RequestError as e:
            print("Could not request results from Google SRS; {0}".format(e))

    def speech_generator(self, response):
        """
        The method is used to convert the sentence to mp3 file. That mp3 file will be used as
        response of the bot to user
        :param response: string answer of the user
        :return:
        """
        speech_object = gTTS(text=response, lang=self.language, slow=False)
        path = os.path.join(self.path_for_music, 'response.mp3')
        speech_object.save(path)
        playsound(path)
        os.remove(path)
