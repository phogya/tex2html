from flask import Flask,render_template,redirect,url_for,request,send_file
import zipfile
import uuid
import os
import io

from cleaner import clean

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#routes
@app.route("/")
def hello_world():
    return render_template("index.html")
    
@app.route("/message/<msg>")
def message(msg):
    return render_template("index.html",message=msg)


@app.route("/convert/",methods=["POST","GET"])
def convert():
    try:
        if request.method=="POST":
            uploaded_file = request.files["latexFile"]
            if uploaded_file:
                input_file = str(uuid.uuid1())+".zip"
                uploaded_file.save(input_file)
                k= extractAndConvert(input_file)
                zip_io= io.BytesIO(open("static/"+k+".zip",'rb').read())
                #zip_data =zipfile.ZipFile(zip_io,'r')
                os.remove("static/"+k+".zip")
                return send_file(zip_io,mimetype="application/zip")
            else:
                return redirect(url_for("message",msg="incorrect file format or empty file"))
        else:
            return redirect(url_for('hello_world'))
    except:
            return redirect(url_for("message",msg="incorrect file format or empty file"))
    
    
@app.route("/sample",methods=["GET"])
def sample():
        return render_template("/sample/index.html")


def extractAndConvert(extractpath):
    file_id=str(uuid.uuid1())
    output_file = file_id
    with zipfile.ZipFile(extractpath,'r') as zp:
        zp.extractall(output_file)

    os.system('''
    latexmlc {}/main.tex --dest={}/index.html --javascript="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js?config=MML_HTMLorMML" '''.format(output_file,output_file))

    kin = open(output_file+'/ltx-article.css','r')
    css = kin.read()
    kin.close()

    customCSS = open('custom.css','r').read()
    css=customCSS+css

    kout= open(output_file+'/ltx-article.css','w')
    kout.write(css)
    kout.close()

    file_in= open(output_file+'/index.html','r')
    file_content = file_in.read()
    file_content = clean(file_content)
    split1,split2=file_content.split("</body>")

    custom_script= '''
      <script>
           function handleScroll() {
            setTimeout(() => {
                window.scrollBy(0, -100);
            }, 500);
            }

            var ele = document.getElementsByClassName("ltx_page_main")[0];
            var imgElement = document.createElement("img");
            imgElement.setAttribute("src", "headerImage.png");
            imgElement.setAttribute("alt", "banner");
            imgElement.setAttribute("style", "width:100% !important;min-height:auto;");
            ele.insertBefore(imgElement, ele.firstChild);

            var docs = document.getElementsByClassName("ltx_note ltx_role_footnote");
            let cnt = 0;
            let footnotes = [];
            let doc = docs[cnt];
            while (cnt < docs.length) {
            footnotes.push(doc.id);
            let inner = doc.childNodes[1];
            let txt = inner.childNodes[0].textContent;
            txt = txt.replace(/  +/g, " ");
            txt = txt.replace("\n", " ");
            if (cnt > 9) footnotes.push(txt.slice(2));
            else footnotes.push(txt.slice(1));
            cnt++;
            doc.innerHTML =
                `<a href="#fn-${cnt}" onClick="handleScroll()">` + doc.innerHTML + "</a>";
            doc = docs[cnt];
            }

            ele = document.getElementsByTagName("article")[0];
            let outer = document.createElement("div", { class: "footnotes-display" });
            let heading = document.createElement("h3");
            heading.appendChild(document.createTextNode("Footnotes"));
            outer.appendChild(heading);

            let j = 0;
            for (let i = 1; i < footnotes.length; i += 2) {
            let p = document.createElement("p");
            p.setAttribute("id", "fn-" + (j + 1));
            let newC = document.createTextNode( footnotes[i]);
            p.appendChild(newC);
            outer.appendChild(p);
            j++;
            }
            ele.appendChild(outer);

            </script>
        </body>
    '''
    html = split1+custom_script+split2
    file_in.close()
    file_out = open(output_file+'/index.html','w')
    file_out.write(html)
    file_out.close()

    os.system('''zip -r ./static/{}.zip {}'''.format(output_file,output_file))
    os.system("rm -rf {}".format(file_id))
    os.remove(extractpath)
    
    return file_id


