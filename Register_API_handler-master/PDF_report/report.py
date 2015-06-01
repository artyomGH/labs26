import urllib2
import os, sys
from subprocess import Popen, PIPE
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

reload(sys)
sys.setdefaultencoding("utf8")

P12_FILE_PATH = 'KapyraKey.p12'
CERT_PASSWORD = "1"
OUTPUT_NAME = "report"


def testator_report(testator):
    return testator.__dict__


def get_report_text():
    text = 'property\n'
    text = text + urllib2.urlopen('http://127.0.0.1:5010/api/property').read().decode()+'\n'




    return text


def gen_pdf(text):
    pdf = SimpleDocTemplate(OUTPUT_NAME + "_unsigned.pdf", pagesize=A4)
    story = []
    style = getSampleStyleSheet()
    paragraphs = text.split('\n')
    for para in paragraphs:
        story.append(Paragraph(para, style['Normal']))
        story.append(Spacer(0, inch * .1))
    pdf.build(story)


def sign_pdf():
    p = Popen(['java', '-jar', 'lib\\jPdfSign.jar', P12_FILE_PATH, OUTPUT_NAME + "_unsigned.pdf", OUTPUT_NAME + ".pdf"],
              stdout=PIPE, stdin=PIPE, stderr=PIPE)
    p.communicate(input=CERT_PASSWORD)

if __name__ == "__main__":
    text = get_report_text()
    gen_pdf(text)
    sign_pdf()
    os.remove(OUTPUT_NAME + "_unsigned.pdf")