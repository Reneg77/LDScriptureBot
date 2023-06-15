import json
import os

import discord
from dotenv import load_dotenv

load_dotenv()
GUILD = os.getenv('DISCORD_GUILD')
TOKEN = os.getenv('DISCORD_TOKEN')

ot = json.load(open('old-testament.json', encoding = 'utf8'))
nt = json.load(open('new-testament.json', encoding = 'utf8'))
bom = json.load(open('book-of-mormon.json', encoding = 'utf8'))
pogp = json.load(open('pearl-of-great-price.json', encoding = 'utf8'))
dnc = json.load(open('doctrine-and-covenants.json', encoding = 'utf8'))
scriptures = [ot, nt, bom, pogp, dnc]

tg = json.load(open('tg.json', encoding = 'utf8'))
bd = json.load(open('bd.json', encoding = 'utf8'))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def process_text(input: str):
    return input.lower().replace(' ', '').replace(',', '').replace('&', '').replace(';', '').replace('-', '')

def get_verse(input: str):
    output = ''
    for scripture in scriptures:
        for book in scripture['books']:
            if 'numbers' in book:
                for number in book['numbers']:
                    for chapter in number['chapters']:
                        if process_text(input) == process_text(chapter['reference']):
                            for verse in chapter['verses']:
                                if output != '':
                                    output += '\n'
                                output += str(verse['verse']) + '.  ' + verse['text'] 
                        for verse in chapter['verses']:
                            if process_text(input) == process_text(verse['reference']):
                                output = verse['text']
            else:
                for chapter in book['chapters']:
                    if process_text(input) == process_text(chapter['reference']):
                        for verse in chapter['verses']:
                            if output != '':
                                output += '\n'
                            output += str(verse['verse']) + '.  ' + verse['text'] 
                    for verse in chapter['verses']:
                        if process_text(input) == process_text(verse['reference']):
                            output = verse['text']
    for entry in tg['topical_guide']:
        if process_text(input) == process_text(entry['name']):
            output = f'[{entry["name"]}](https://www.churchofjesuschrist.org/{entry["link"]})'
    for entry in bd['bible_dictionary']:
        if process_text(input) == process_text(entry['name']):
            output = f'[{entry["name"]}](https://www.churchofjesuschrist.org/{entry["link"]})'

    return output

@client.event
async def on_ready():
    print(f'{client.user} is connected to the following guilds:')
    for guild in client.guilds:
        print(f'{guild.name}(id: {guild.id})')
    

@client.event
async def on_message(message: discord.message):
    content = message.clean_content
    if '[' and ']' in content:
        misinputs = []
        text = ''
        for start in range(0, len(content)):
            if content[start] == '[':
                found = False
                for end in range(start+1, len(content)):
                    if content[end] == ']' and not found:
                        found = True
                        verses = content[start+1:end]
                        input = verses
                        if '-' in verses:
                            for char in range(0, len(verses)):
                                if verses[char] == ' ' or verses[char] == ':':
                                    start_Index = char
                                if verses[char] == '-':
                                    divider_Index = char
                            start_No = verses[start_Index+1:divider_Index]
                            end_No = verses[divider_Index+1:len(verses)]
                            result = ''
                            for number in range(int(start_No), int(end_No)+1):
                                verse = verses[0:start_Index+1] + str(number)
                                result += get_verse(verse)
                                if result != '':
                                    result = '\n' + str(number) + '.  ' + result
                            if result != '':
                                if text != '':
                                    text += '\n\n'
                                text += verses + ':' + result
                            else:
                                misinputs += [input]
                        else:
                            result = get_verse(verses[0:len(verses)])
                            if result != '':
                                if text != '':
                                    text += '\n\n'
                                text += verses + ':\n' + result
                            else:
                                misinputs += [input]

        if text != '':
            embed = discord.Embed()
            embed.color = discord.Color.from_rgb(15, 110, 150)
            embed.title = 'References:'
            if len(text) > 4096:
                messages = []
                count = 0
                max = int(len(text)/4096)
                while len(text) > 4096:
                    count += 1
                    embed.description = text[0:4096]
                    embed.title = 'References: (' + str(count) + '/' + str(max) + ')'
                    await message.channel.send(embed = embed)
                    text = text[4096:len(text)]
                embed.description = text
                embed.title = 'References: (' + str(max) + '/' + str(max) + ')'
                await message.channel.send(embed=embed)
            else:
                embed.description = text
                await message.channel.send(embed=embed)

        if len(misinputs) > 0:
            embed = discord.Embed()
            embed.color = discord.Color.from_rgb(150, 50, 50)
            embed.title = 'Hmm,'
            if len(misinputs) > 1:
                embed.description = f'I couldn\'t find that. Check for mispellings in the following inputs:'
            else:
                embed.description = f'I couldn\'t find that. Check for mispellings in the following input:'
            for misinput in misinputs:
                embed.description += f'\n*{misinput}*'
            await message.channel.send(embed=embed)


client.run(TOKEN)