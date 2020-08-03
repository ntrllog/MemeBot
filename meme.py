import discord, requests, textwrap, sys, os
from text_wrap import text_wrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name='Type !meme for help'))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!meme help') or message.content == '!meme':
        embed = displayHelp()
        await message.channel.send(embed=embed)

    elif message.content.startswith('!meme'):
        if not message.attachments:
            await message.channel.send('No image selected')
            return
        try:
            content = list(map(str.strip, message.content.split(';')))
            image = getImageFromURL(message.attachments[0].url)
            addTextToImage(image, *content[1:])
            b = createFile(image)
        except Exception as e:
            embed = discord.Embed(title='Invalid command', color = 0x00ff00)
            embed.add_field(name='Error message', value=str(e), inline=False)
            embed.add_field(name='Command entered', value=message.content, inline=False)
            await message.channel.send(embed=embed)
            return
        await message.channel.send(file=discord.File(b, filename='image.jpg'))

def createFile(im):
    b = BytesIO()
    im.save(b, 'JPEG')
    b.seek(0)
    return b

def getImageFromURL(url):
    response = requests.get(url, stream=True)
    return Image.open(response.raw).convert('RGB')

def addTextToImage(im, t1='', t2='', t1Color='black', t2Color='black'):
    imWidth, imHeight = im.size
    fontsize = int(imHeight * .05)

    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(os.path.join('fonts', 'arial.ttf'), fontsize)
    
    t1Lines = text_wrap(t1, font, int(imWidth * .9))
    t2Lines = text_wrap(t2, font, int(imWidth * .9))

    text_height = 0
    for line in t1Lines:
        t1Width, t1Height = font.getsize(line)
        draw.multiline_text(((imWidth-t1Width)/2, text_height), line, fill=t1Color, font=font)
        text_height += t1Height

    text_height = imHeight - imHeight * .1
    for line in t2Lines:
        t2Width, t2Height = font.getsize(line)
        draw.multiline_text(((imWidth-t2Width)/2, text_height), line, fill=t2Color, font=font)
        text_height += t2Height

def displayHelp():
    pcCommand = 'Send a picture and add the comment: "!meme; top_text; bottom_text"'
    mobileCommand = 'Select a picture to send, switch to keyboard, and add the message: "!meme; top_text; bottom_text"'
    topTextOnlyCommand = '!meme; top_text'
    bottomTextOnlyCommand = '!meme;; bottom_text'
    colorCommand = '!meme; top_text; bottom_text; top_text_color; bottom_text_color'
    embed = discord.Embed(title='For Dummies', color = 0x00ff00)
    embed.add_field(name='On PC', value=pcCommand, inline=False)
    embed.add_field(name='On mobile', value=mobileCommand, inline=False)
    embed.add_field(name='Put text on top only', value=topTextOnlyCommand, inline=False)
    embed.add_field(name='Put text on bottom only', value=bottomTextOnlyCommand, inline=False)
    embed.add_field(name='Change text color', value=colorCommand, inline=False)
    return embed

client.run(os.getenv('TOKEN'))
