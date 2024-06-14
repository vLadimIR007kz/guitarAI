import acrcloud
import requests
import streamlit as st
from st_audiorec import st_audiorec
import os
import toml

@st.cache_data
def get_GPT_answer(artist_name:str, song_name:str):
	comment = ""
	url = "https://api.openai.com/v1/chat/completions"
	api_key =config1['chatGPTsecret']
	if simplifychords:
		simplify="simplified"
	else:
		simplify="unsimplified"

	if usebarrechords:
		barre="barre"
	else:
		barre="no barre"

	if simplifestrum:
		ss="simplified"
	else:
		ss="unsimplified"

	if showstrum:
		strum="guitar strum"
	else:
		strum="guitar fingerpicking"

	if tabulatureforchords:
		tabulature="and full tabulature for chords"
	else:
		tabulature=" do not include tabulature"

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {api_key}"
	}
	data = {
		"model": "gpt-4",
		"messages": [{
			"role": "user",
			"content": "give" +simplify+" "+barre+" guitar chords for whole text of "+song_name+" of " +artist_name+" . Include text "+ss+" "+strum+" "+tabulature+". Use answer patter: tabulature(if asked), exact strum or fingerpicking pattern, chords+full text of the song, including all verses, chorus, pre-chorus and bridge, if they are presented in the song, do not include any other advices or recommendations for play",
		}],
		"max_tokens": 4000
	}
	print("give" +simplify+" "+barre+" guitar chords for whole text of "+song_name+" of " +artist_name+" . Include text "+ss+" "+strum+" "+tabulature+". Use answer patter: tabulature(if asken), strum or fingerpicking with exact instructions, chords+text")
	try:
		response = requests.post(url, json=data, headers=headers)
		response.raise_for_status()

		response_data = response.json()
		print(response_data)
		if 'choices' in response_data and len(response_data['choices']) > 0:
			choice = response_data['choices'][0]
			if 'message' in choice and 'content' in choice['message']:
				text_response_data = choice['message']['content']
				print(text_response_data)
				# percent = re.search(r'\b\d{2}\b', text_response_data).group()
				# lines = response_data['choices'][0]['message']['content'].split('\n')
				# lines_without_first_two = lines[2:]
				# comment = '\n'.join(lines_without_first_two)
				comment = text_response_data

			else:
				print("Ошибка: Ключ 'message' или 'content' отсутствует в результате")
		else:
			print("Результат не содержит данных")
	except requests.exceptions.HTTPError as err:
		print(f"HTTP ошибка: {err}")
	except Exception as err:
		print(f"Ошибка: {err}")

	return comment
with open('main.toml', 'r') as f:
	config1=toml.load(f)
config = {
	"key": config1['ACRcloudkey'],
	"secret": config1['ACRcloudsecret'],
	"host": config1['ACRcloudhost']

}
acr = acrcloud.ACRcloud(config)
st.write('song recognition')
wav_audio_data = st_audiorec()
simplifychords=st.checkbox("Do you want to recieve simplified chords?")
showstrum=st.checkbox("Strum or fingerpicking?")
simplifestrum=st.checkbox("Simplify rithm?")
usebarrechords=st.checkbox("Should we use barre chords?")
tabulatureforchords=st.checkbox("Do you need tabulature for chords?")
artistname=st.text_input("Write here name of the artist")
songname=st.text_input("Write here song name")
button=st.button("click here to send query")
if button:
	an=st.write('')
	sn=st.write('')
	main=st.write('')
	an=st.text(artistname)
	sn=st.text(songname)
	main=st.text(get_GPT_answer(artistname, songname))




if wav_audio_data is not None:
	an = st.write('')
	sn = st.write('')
	main = st.write('')
	try:
		with open('myfile.wav', mode='bx') as f:
			f.write(wav_audio_data)
	except:
		os.remove('myfile.wav')
		with open('myfile.wav', mode='bx') as f:
			f.write(wav_audio_data)
	audio = 'myfile.wav'
	answer = acr.recognize_audio(audio)
	artist_name = answer.get('metadata').get('music')[0].get('artists')[0].get('name')
	song_name = answer.get('metadata').get('music')[0].get('title')
	an=st.text(artist_name)
	sn=st.text(song_name)
	main=st.text(get_GPT_answer(artist_name,song_name))
	os.remove('myfile.wav')