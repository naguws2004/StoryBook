from flask import Flask, request, render_template_string, render_template
import requests
import json

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
            <title>Select Options</title>
            <style>
                .form-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .form-table {
                    margin: 0 auto;
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
            <form action="/generateStoryBook" method="post" class="form-container" onsubmit="return validateForm()">
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
                                <option value="2">2</option>
                                <option value="4">4</option>
                                <option value="6">6</option>
                                <option value="8">8</option>
                                <option value="10">10</option>
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
                    <input type="submit" value="Submit Options">

                    <!-- Reset Button -->
                    <input type="reset" value="Reset">
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

    # Process the form data as needed
    return render_song_form(generated_story)

def render_song_form(generated_story):
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Song Lyrics</title>
            <style>
                .form-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .form-table {
                    margin: 0 auto;
                }
                .field-width {
                    width: 250px;
                }
            </style>
        </head>
        <body>
            <form action="/generatePDF" method="post" class="form-container">
                <h1>Story Book</h1>
                <h2>Story Board</h2>
                <div><textarea id="txtStory" name="txtStory" style="vertical-align:middle;" rows="10" cols="75">{{ generated_story }}</textarea></div><br/>
                <h2>Illustrations</h2>
                <div>Images</div><br/>
                <!-- Submit Button -->
                <div>
                <input type="submit" value="Generate PDF">
                <input type="button" onclick="history.back()" value="Back">
                </div>
            </form>
        </body>
        </html>
    ''', generated_story=generated_story)

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
