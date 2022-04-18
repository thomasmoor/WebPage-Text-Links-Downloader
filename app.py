from flask import Flask, json, jsonify, redirect, render_template, request, session, make_response, url_for
from flask_session import Session
from flask_cors import CORS, cross_origin
import lxml.html as lh
import requests

app = Flask(__name__)

# Using session to avoid a "Confirm Form Resubmission" pop-up:
# Redirect and pass form values from post to get method
# app.secret_key = 'my_secret_key'
app.config['SECRET_KEY'] = "your_secret_key" 
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT']= False
app.config.from_object(__name__)
Session(app)

# Enable Cross-Origin Resource Sharing for API use from another IP and/or port
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def extract(url):

  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

  # Retrieve the data
  response = requests.get(url,headers=headers)
  status=response.status_code
  if status!=200:
    print(response.content)
    print(url)
    print(f"Error: {status}")
    return f"Error: {status}"

  doc = lh.fromstring(response.content)
  # print(f"doc length:{len(doc)}")
  
  els = doc.xpath('//*')
  s=""
  inBody=False
  inHREF=False
  l=""
  pTag=""
  for e in els:
    s1=""
    
    # Get text only after the <body> tag
    tag=e.tag
    if tag == 'body':
      inBody=True
      continue
    if not inBody:
      continue
    if tag=='script':
      continue
      
    # Get the link     
    href = e.get('href')
    if href:
      inHREF=True
    
    # Get the text
    text=e.text
      
    # No href or text
    if (not href or len(href.strip())==0) and (not text or len(text.strip())==0):
      continue

    # Output the text
    if text and len(text.strip())>0:
      s1+=text.strip()

    # Output the href
    if inHREF:
      s1+=" < "+href+" > "
      inHREF=False
      
    # print(s1)
 
    # Append to the output
    # if len(s) > 0 and s[-1] in ['.','?','!']:
    #  s+='\n'
    # elif len(s) > 0:
    s+='\n'
    s+=s1

    # Value of the previous tag, 
    # to try and improve the display
    pTag=tag
    
  # for e
  # print(f"doc length 2:{len(doc)}")
  
  return s
# get_url_text

def url_ok(url):
  if url=="":
    return False
  return True

# HTML home page
@app.route('/', methods=['GET','POST'])
def slash():
  print(f"slash - got request: {request.method}")

  # Default text
  text='Enter or copy/paste a URL in the box above \nand press "Get Text"'

  # Extract request
  if 'extract' in request.form:
    url = request.form["url"]
    print(f"Branch: extract - url: {url}")
    # Get the text
    if url_ok(url):
      text=extract(url)
      print(f"text len={len(text)}")
      print(text)
    else:
      text="Could not get web page contents"
      
  # Download request
  elif 'download' in request.form:
    text=request.form['text']
    print(f"Branch: Download - text len={len(text)}")
    output = make_response(text)
    output.headers["Content-Disposition"] = "attachment; filename=export.txt"
    output.headers["Content-type"] = "text/csv"
    return output

  # Redirect to avoid "Form Resubmission" pop-up
  if request.method=='POST':
    print(f"branch: redirect - text length: {len(text)}")
    session['text'] = text
    return redirect(url_for('slash'))
  
  # Render page
  else:
    text=session.get('text','text variable not found in session')
    print(f"render index.html text length= {len(text)}")
    return render_template("index.html", text=text)  

if __name__ == '__main__':
  app.run()