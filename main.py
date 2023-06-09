import ftplib
import shutil
from flask import Flask, jsonify, render_template,send_from_directory
from flask_cors import CORS
import pandas
import os
from flask_mail import Mail,Message





ENV = os.getenv("FLASK_ENV")
static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../public/')

ftp_server =  os.getenv('FTP_SERVER')
ftp_user_name =  os.getenv('FTP_USER_NAME')
ftp_port =  os.getenv('FTP_PORT')
ftp_password =  os.getenv('FTP_PASSWORD')

app = Flask(__name__)
# app = Flask(__name__, static_folder="./build/static", template_folder="./build")



CORS(app)

# Configuración de Flask-Mail


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')


mail = Mail(app)




@app.route('/')
def sitemap():
    return send_from_directory(static_file_dir, 'index.html')


@app.route('/<path:path>', methods=['GET'])
def serve_any_other_file(path):
    if not os.path.isfile(os.path.join(static_file_dir, path)):
        path = 'index.html'
    response = send_from_directory(static_file_dir, path)
    response.cache_control.max_age = 0 # avoid cache memory
    return response



def getData(name, sheet_name):
    ftp = ftplib.FTP()
    ftp.connect(ftp_server,21)
    ftp.login(ftp_user_name,ftp_password)
    ftp.cwd("Excels")
    fnames = ftp.nlst()
    with open(f"./{name}", "wb") as file:
        retCode= ftp.retrbinary(f"RETR {name}", file.write)
    ftp.quit()
    if(sheet_name):
        src_path = os.path.join(os.getcwd(), name)
        excel_data_df = pandas.read_excel(src_path, sheet_name=sheet_name)
    else:
        src_path = os.path.join(os.getcwd(), name)
        excel_data_df = pandas.read_excel(src_path)

    json_str =  excel_data_df.to_json(orient='records')
    return json_str



@app.route("/getExcel/<name>")
def getExcel(name):
    json_str= (getData(name,None)) 

    try:
        return jsonify(json_str), 200
    except:
        print(404)


def send_email(to, subject, body):
    msg = Message(subject=subject,
                  recipients=[to],
                  body=body)

    mail.send(msg)



@app.route("/get_VA_data/<name>/<sheet_name>")
def get_VA_data(name,sheet_name):
    json_str= (getData(name, sheet_name)) 

    try:
        return jsonify(json_str), 200
    except:
        print(404)


def send_email(to, subject, body):
    msg = Message(subject=subject,
                  recipients=[to],
                  body=body)

    mail.send(msg)






@app.route('/enviar-email', methods=['GET'])
def enviar_email():
    
    try:
        email_destino = 'jesus.golineuro@gmail.com'
        asunto = 'Correo de prueba'
        cuerpo = 'Este es un correo de prueba enviado con Flask-Mail'

        send_email(to=email_destino, 
                   subject=asunto, 
                   body=cuerpo)

        return "El correo se ha enviado correctamente."
    except Exception as e:
        return(str(e))





# if __name__=="__main__":
#     # app.run(debug=False)
#     app.run(port= 5000, debug=True)

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=PORT, debug=True)





