#import pdfkit
#import base64

#"C:\Program Files\Python37\Lib\site-packages\wkhtmltopdf"
#config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
#def to_pdf(filename):
#    pdfkit.from_string(filename,'example.pdf', configuration=config)

#def create_download_link(val, filename):
#    b64 = base64.b64encode(val)  # val looks like b'...'
#    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

# importing PdfFileWriter class
#from PyPDF2 import PdfFileWriter as w
#import fpdf
from fpdf import FPDF, HTMLMixin
#import imgkit


class PDF(FPDF , HTMLMixin):
     pass # nothing happens when it is executed.

def to_pdf(df):
    pdf = PDF()#pdf object
    #First page
    pdf.add_page()
    pdf.write_html(df)
    #pdf.output(f'{filename}.pdf', 'F')


#pdf=PDF(orientation='L') # landscape

#def to_pdf(filename,a):
#    imgkit.from_file(a, 'test.jpg')
    #pdf = FPDF(format='letter') #pdf format
    #pdf.add_page() #create new page
    #pdf.set_font("Arial", size=12) # font and textsize
    #pdf.normalize_text(a)
    #pdf.text(1,10,a)
    #pdf.cell(200, 10, txt=a[0], ln=1, align="L")
    #pdf.cell(200, 10, txt=a[1], ln=2, align="L")
    #pdf.cell(200, 10, txt=a[2], ln=3, align="L")
    #pdf.output(f"{filename}.pdf")


