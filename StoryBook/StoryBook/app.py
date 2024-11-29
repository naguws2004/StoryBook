from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
import requests
import json
import os
import re

import torch
# from diffusers import StableDiffusionPipeline
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

@app.route('/')
def index():
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Story Book</title>
            <style>
                .form-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .form-table {
                    margin: 50 auto;
                }
                .field-width {
                    width: 350px;
                }
                .field-firsthalfwidth {
                    width: 100px;
                }
                .field-secondhalfwidth {
                    width: 246px;
                }
            </style>
            <script>
                function validateForm() {
                    var txtPrompt = document.getElementById('txtPrompt').value;
                    var txtTheme = document.getElementById('txtTheme').value;
                    var txtWords = document.getElementById('txtWords').value;
                    var txtStyle = document.getElementById('txtStyle').value;
                    var txtIllustrations = document.getElementById('txtIllustrations').value;
                    
                    if (txtPrompt.trim() === '') {
                        alert('Story Prompt cannot be empty.');
                        return false;
                    }
                    if (txtTheme.trim() === '') {
                        alert('Story Theme cannot be empty.');
                        return false;
                    }
                    if (txtWords.trim() === '') {
                        alert('Story Length cannot be empty.');
                        return false;
                    }
                    if (txtStyle.trim() === '') {
                        alert('Story Image Style cannot be empty.');
                        return false;
                    }
                    if (txtIllustrations.trim() === '') {
                        alert('Story No. of Illustrations cannot be empty.');
                        return false;
                    }
                    return true;
                }
            </script>
        </head>
        <body>
            <form id="myForm" name="myForm" action="/generateStoryBook" method="post" class="form-container">
                <h1>Story Book</h1>
                <h2>Select Options</h2>
                <table class="form-table">
                    <tr>
                        <td>
                            <label for="lblPrompt">Prompt:</label>
                        </td>
                        <td>
                            <input type="text" id="txtPrompt" name="txtPrompt" class="field-width" placeholder="example: A brave little dragon who loves to bake">
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <label for="lblTheme">Theme:</label>
                        </td>
                        <td colspan="2">
                            <input type="text" id="txtTheme" name="txtTheme" class="field-firsthalfwidth" placeholder="Select or type...">
                            <select id="lstTheme" name="lstTheme" class="field-secondhalfwidth">
                                <option value="">Select a Theme</option>
                                <option value="Fairy Tale">Fairy Tale</option>
                                <option value="Adventure">Adventure</option>
                                <option value="Fantasy">Fantasy</option>
                                <option value="Freedom">Freedom</option>
                                <option value="Friendship">Friendship</option>
                                <option value="Bravery">Bravery</option>
                                <option value="Happiness">Happiness</option>
                                <option value="Kindness">Kindness</option>
                                <option value="Trust">Trust</option>
                                <option value="Childhood">Childhood</option>
                                <option value="Crime">Crime</option>
                                <option value="Dreams">Dreams</option>
                            </select>
                            <script>
                                const lstThemeElement = document.getElementById('lstTheme');
                                const txtThemeElement = document.getElementById('txtTheme');

                                lstThemeElement.addEventListener('change', () => {
                                    txtThemeElement.value = lstThemeElement.value;
                                });
                            </script>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <label for="lblWords">Word Length:</label>
                        </td>
                        <td colspan="2">
                            <input type="text" id="txtWords" name="txtWords" class="field-firsthalfwidth" placeholder="Select or type...">
                            <select id="lstWords" name="lstWords" class="field-secondhalfwidth">
                                <option value="">Select Word Length</option>
                                <option value="50">50</option>
                                <option value="100">100</option>
                                <option value="150">150</option>
                                <option value="200">200</option>
                                <option value="250">250</option>
                                <option value="300">300</option>
                                <option value="500">500</option>
                                <option value="1000">1000</option>
                            </select>
                            <script>
                                const lstWordsElement = document.getElementById('lstWords');
                                const txtWordsElement = document.getElementById('txtWords');

                                lstWordsElement.addEventListener('change', () => {
                                    txtWordsElement.value = lstWordsElement.value;
                                });
                            </script>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <label for="lblStyle">Art Style:</label>
                        </td>
                        <td colspan="2">
                            <input type="text" id="txtStyle" name="txtStyle" class="field-firsthalfwidth" placeholder="Select or type...">
                            <select id="lstStyle" name="lstStyle" class="field-secondhalfwidth">
                                <option value="">Select Style</option>
                                <option value="Cartoon">Cartoon</option>
                                <option value="Realistic">Realistic</option>
                                <option value="Anime">Anime</option>
                            </select>
                            <script>
                                const lstStyleElement = document.getElementById('lstStyle');
                                const txtStyleElement = document.getElementById('txtStyle');

                                lstStyleElement.addEventListener('change', () => {
                                    txtStyleElement.value = lstStyleElement.value;
                                });
                            </script>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <label for="lblIllustrations">No. of Illustrations:</label>
                        </td>
                        <td colspan="2">
                            <input type="text" id="txtIllustrations" name="txtIllustrations" class="field-firsthalfwidth" placeholder="Select or type...">
                            <select id="lstIllustrations" name="lstIllustrations" class="field-secondhalfwidth">
                                <option value="">Select No. of Illustrations</option>
                                <option value="1">1</option>
                                <option value="3">3</option>
                                <option value="5">5</option>
                            </select>
                            <script>
                                const lstIllustrationsElement = document.getElementById('lstIllustrations');
                                const txtIllustrationsElement = document.getElementById('txtIllustrations');

                                lstIllustrationsElement.addEventListener('change', () => {
                                    txtIllustrationsElement.value = lstIllustrationsElement.value;
                                });
                            </script>
                        </td>
                    </tr>
                </table>
                <p>
                    <!-- Submit Button -->
                    <input id="btnSubmit" name="btnSubmit" type="submit" value="Submit Options">
                    <script>
                        const submitButton = document.getElementById('btnSubmit');
                        const form = document.getElementById('myForm'); 

                        submitButton.addEventListener('click', () => {
                            // Prevent default form submission behavior
                            event.preventDefault();
                            
                            if (validateForm()) {
                                // Submit the form
                                form.submit();
                            }
                        });
                    </script>
                    <!-- Reset Button -->
                    <input id="btnReset" name="btnReset" type="reset" value="Reset">
                    <script>
                        const resetButton = document.getElementById('btnReset');
                        const form = document.getElementById('myForm'); 

                        resetButton.addEventListener('click', function() {
                            // Reset the form
                            form.reset();
                        });
                  </script>
                </p>
            </form>
        </body>
        </html>
    '''

@app.route('/generateStoryBook', methods=['POST'])
def generateStoryBook():
    txtPrompt = request.form.get('txtPrompt')
    txtTheme = request.form.get('txtTheme')
    txtWords = request.form.get('txtWords')
    txtStyle = request.form.get('txtStyle')
    txtIllustrations = request.form.get('txtIllustrations')
    
    # Generate text
    prompt = f"Write a story on: {txtPrompt}. Story should be based on theme: {txtTheme}. Story should contain {txtWords} number of words."
    
    generated_story = generate_text(prompt)

    # generated_story = "In a lush valley, a tiny dragon named Spark loved to play. \nUnlike others, Spark was fearless, always seeking new adventures. \nOne sunny morning, Spark discovered a cave hidden behind a waterfall. \nIgnoring the warnings of his friends, he ventured inside. \nThe cave was dark and echoed with mysterious sounds. \nSpark\'s heart raced with excitement. \nDeeper in, he found an old, dusty map. It led to the legendary Crystal Cavern. \nWith the map in his claws, Spark embarked on a quest, facing riddles and traps, until he finally beheld the shimmering crystals, proving that bravery and curiosity lead to the greatest adventures."

    # Generate cover image
    cover_imageprompt = f"{txtPrompt}. theme: {txtTheme}. art style: {txtStyle}"

    # Generate images
    imageprompt = f"theme: {txtTheme}. art style: {txtStyle}. {generated_story}"

    image_urls = generate_image(cover_imageprompt, imageprompt, int(txtIllustrations))

    # Process the form data as needed
    return render_story_form(generated_story, image_urls)

def generate_text(prompt):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
      "Authorization": "Bearer xai-P2VrBOBKw2Z2apm7eu5CA0s6ryOf9E32rNfnXVmmuafPvLWsX4G8eaXLBtgTvFd86kgMDyeyQ0JN1akK",
      "Content-Type": "application/json"
    }
    data = {
        "model": "grok-beta",
        "messages": [
        { "role": "user", "content": prompt }
        ],
        "temperature": 0,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        response_json = json.loads(response.text)
        generated_story = response_json['choices'][0]['message']['content'].strip()
    else:
        generated_story = 'Error generating story.'
    
    return generated_story

# Generate image from text 
def generate_image(cover_imageprompt, imageprompt, n):
    # model_id = "stabilityai/stable-diffusion-2-1"

    # # Use the DPMSolverMultistepScheduler (DPM-Solver++) scheduler here instead
    # pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    # pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    # pipe = pipe.to("cuda")

    image_urls = ["", "", "", "", "", "", ""]
    images = ["", "", "", "", "", ""]
    # images = pipe(cover_imageprompt, guidance_scale=7.5, num_inference_steps=50, num_images_per_prompt=1)
    # images[0].save(f"images/image_0.png")
    # image_urls[0] = images[0]
    image_urls[0] = f"image_0.jpeg"
    # images = pipe(imageprompt, guidance_scale=7.5, num_inference_steps=50, num_images_per_prompt=n)
    i = 1
    for image in images:
        # image.save(f"images/image_{i}.png")
        image_urls[i] = f"images/image_{i}.jpeg"
        i = i + 1
    
    return image_urls

def render_story_form(generated_story, image_urls):
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Story Book</title>
            <style>
                .form-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .form-table {
                    margin: 50 auto;
                }
                .field-width {
                    width: 250px;
                }
                .cover-image-width {
                    width: 200px;
                    height: 250px;
                }
                .image-width {
                    width: 100px;
                    height: 150px;
                }
            </style>
        </head>
        <body>
            <form action="/generatePDF" method="post" class="form-container">
                <h1>Story Book</h1>
                <h2>Story Board</h2>
                <div><textarea id="txtStory" name="txtStory" style="vertical-align:middle;" rows="10" cols="75">{{ generated_story }}</textarea></div><br/>
                <h2>Illustrations</h2>
                <h3>Cover Picture</h3>
                <div><img src="{{ url_for('static', filename='images/image_0.jpeg') }}" class="cover-image-width" alt="Cover Image"></div><br/>
                <h3>Other Pictures</h3>
                <div>
                    <table class="form-table">
                        <tr>
                            <td>
                                {% if image_urls[1] == "" %}
                                    <img src="" alt="Blank Image">
                                {% else %}
                                    <img src="{{ url_for('static', filename='images/image_1.jpeg') }}" class="image-width" alt="First Image">
                                {% endif %}
                            </td>
                            <td>
                                {% if image_urls[2] == "" %}
                                    <img src="" alt="Blank Image">
                                {% else %}
                                    <img src="{{ url_for('static', filename='images/image_2.jpeg') }}" class="image-width" alt="Second Image">
                                {% endif %}
                            </td>
                            <td>
                                {% if image_urls[3] == "" %}
                                    <img src="" alt="Blank Image">
                                {% else %}
                                    <img src="{{ url_for('static', filename='images/image_3.jpeg') }}" class="image-width" alt="Third Image">
                                {% endif %}
                            </td>
                        <tr>
                        <tr>
                            <td>
                                {% if image_urls[4] == "" %}
                                    <img src="" alt="Blank Image">
                                {% else %}
                                    <img src="{{ url_for('static', filename='images/image_4.jpeg') }}" class="image-width" alt="Fourth Image">
                                {% endif %}
                            </td>
                            <td>
                                {% if image_urls[5] == "" %}
                                    <img src="" alt="Blank Image">
                                {% else %}
                                    <img src="{{ url_for('static', filename='images/image_5.jpeg') }}" class="image-width" alt="Fifth Image">
                                {% endif %}
                            </td>
                            <td>
                                {% if image_urls[6] == "" %}
                                    <img src="" alt="Blank Image">
                                {% else %}
                                    <img src="{{ url_for('static', filename='images/image_6.jpeg') }}" class="image-width" alt="Sixth Image">
                                {% endif %}
                            </td>
                        <tr>
                    </table>
                </div><br/>
                <!-- Submit Button -->
                <div>
                    <input type="submit" value="Generate PDF">
                    <input type="button" onclick="history.back()" value="Back">
                </div>
            </form>
        </body>
        </html>
    ''', generated_story=generated_story, image_urls=image_urls)

@app.route('/generatePDF', methods=['POST'])
def generatePDF():
    txtStory = request.form.get('txtStory')
    paras = re.split(r'\n+', txtStory)
    image_path = os.path.join("static", "images/image_0.jpeg")
    create_pdf(paras)

    return render_story_download()

def create_pdf(paras):
    doc = SimpleDocTemplate(os.path.join("static", "output.pdf"),pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)
    Story=[]
    cover_image = os.path.join("static", "images/image_0.jpeg")
    im = Image(cover_image, 7*inch, 9*inch)
    Story.append(im)
    Story.append(Spacer(1, 12))
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
    i = 1
    for para in paras:
        Story.append(Paragraph(para, styles["Normal"]))
        Story.append(Spacer(1, 12))
        image = os.path.join("static", f"images/image_{i}.jpeg")
        try:
            # Code that might raise an exception
            im = Image(image, 3*inch, 3*inch)
            Story.append(im)
            Story.append(Spacer(1, 12))
        except Exception:
            # Code to handle the exception
            pass  # Silently ignore the exception
        i = i + 1
    
    doc.build(Story)

def render_story_download():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Story Book</title>
        </head>
        <body>
            <h1>Story Book</h1>
            <p>
                <a href="{{ url_for('static', filename='output.pdf') }}">Download File</a>
            </p>
        </body>
        </html>
    ''')

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
