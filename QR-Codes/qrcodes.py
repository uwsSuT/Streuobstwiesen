from reportlab.pdfgen import canvas   
import pyqrcode
from reportlab.graphics import renderSVG    
from reportlab.graphics.shapes import Image, Drawing, Rect, Line, String
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.graphics import renderPDF

from pprint import pformat
from schtob.lib.dbg import dprint
from obstsorten.defs import qr_text4sorte

URL_base = "https://hilgi-docker.herokuapp.com/wiese/baum/"

class qr_codes():

    def __init__(self, qr_infos, pdf_name="/tmp/qrcodes.pdf", verbose=0):

        self.qr_infos = qr_infos
        self.verbose = verbose

        self.c = canvas.Canvas(pdf_name)
        self.x = 5*mm
        self.y = 5*mm
        self.fontname = "Helvetica-BoldOblique"
        self.fontsize = 24
        self.c.setFont(self.fontname, self.fontsize)
        self.draw_dim = 90*mm
        self.rect_dim = 83*mm
        self.qr_dim = self.rect_dim - (3 * self.fontsize)
        self.qr_x_offset = (self.rect_dim - self.qr_dim ) / 2
        self.qr_y_offset = 3*mm
        self.act_x = self.x
        self.act_y = self.y
        self.nr_y = self.rect_dim - self.fontsize

        self.baum_nr = 0
        self.baum_per_page = 6

    def gen_pdf(self):
        """
            Generiere für die übergebene BaumInfo ein PDF-Dokument

            die HauptFunktion der Class, alle anderen Funktionen sind
            eigentlich nur interne Funktionen

        """
        dprint("gen_pdf: ")
        for baum in self.qr_infos.baum_infos:
            if self.verbose:
                print("gen_pdf: baum: %s" % pformat(baum))
            if self.baum_nr == 0:
                self.c.translate(self.x, self.y)
            self.add_baum(self.qr_infos.baum_infos[baum])
            self.baum_nr += 1
            if self.baum_nr == self.baum_per_page:
                self.baum_nr = 0
                self.act_y = self.y
                self.c.showPage()
            elif self.baum_nr % 2:
                self.c.translate(self.draw_dim, 0)
            elif self.baum_nr:
                self.c.translate(-(self.draw_dim),
                                 self.draw_dim)
            else:
                print("self.baum_nr: %s else" % self.baum_nr)
        self.c.save()

    def add_baum(self, baum):
        """
            Zeichne den Barcode, die Baum-Nr, Sorten-Name und einen Rahmen
        """
        dprint("add_baum: %s" % pformat(baum))
        if self.verbose:
            print("nr: %s sorte: <%s>" % (baum['nr'], baum['sorte']))

        self.d = Drawing(self.draw_dim, self.draw_dim)
        self.draw_nr(baum)
        self.draw_sorte(baum)
        self.draw_bc(baum)

    def get_qr_name(self, sorte):
        """
            Hol den Namen für die Sorte aus dem "defs" file
        """
        if sorte in qr_text4sorte:
            return qr_text4sorte[sorte]
        if '\n' in sorte:
            nsorte = sorte.replace('\n', '')
            if nsorte in qr_text4sorte:
                return qr_text4sorte[nsorte]
        return sorte

    def draw_nr(self, baum):
        """
            Schreib die Nr in dem aktuellen Drawing
            berechne die X-Position aus der Breite des Strings un der 
            Breite des Drawings
            Die Y-Position ist in der Class Defined
        """
        txt = "%s" % baum['nr']
        x = (self.rect_dim - stringWidth(
                                        txt, self.fontname, self.fontsize)
               ) / 2
        self.d.add(String(x, self.nr_y, txt,
                        fontName=self.fontname,
                        fontSize=self.fontsize))

    def draw_sorte(self, baum):
        """
            Schreib die Sorte in dem aktuellen Drawing
            berechne die X-Position aus der Breite des Strings un der 
            Breite des Drawings
            Die Y-Position ist in der Class Defined
        """
        txt = self.get_qr_name(baum['sorte'])
        nr_x = (self.rect_dim - stringWidth(
                                        txt, self.fontname, self.fontsize)
               ) / 2
        self.d.add(String(nr_x,
                        self.nr_y - self.fontsize - (self.qr_y_offset/2),
                        txt,
                        fontName=self.fontname,
                        fontSize=self.fontsize))

    def draw_bc(self, baum):
        """
            Zeichne den Rahmen und den Barcode in das aktuelle Drawing
        """
        self.d.add(Rect(0, 0, self.rect_dim, self.rect_dim, strokeWidth=1,
                   strokeColor=colors.black, fillColor=None))
        self.d.add(QrCodeWidget(value=URL_base + "%s/" % baum['nr'],
              x=self.qr_x_offset,
              y=self.qr_y_offset,
              barHeight=self.qr_dim,
              barWidth=self.qr_dim,
              barBorder=0))
        renderPDF.draw(self.d, self.c, 0, 0)

if __name__ == '__main__':

    pass

