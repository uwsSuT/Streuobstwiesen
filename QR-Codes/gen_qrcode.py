#!/usr/bin/python3

import sys
from os import makedirs
from os.path import basename, join, exists, isdir
import fpdf
import getopt
from pprint import pformat
import qrencode
from fpdf import FPDF

from schtob.lib.dbg import dprint
from init_db.wiese import Wiesen, BaumInfos, ObstInfos
from obstsorten.defs import qr_text4sorte

base_dir = "../init_db"
WiesenFile = join(base_dir, 'wiesen.txt')
BaumJson = join(base_dir, 'Baeume.geojson')
ObstSorten = join(base_dir, 'Obstsorten.csv')

URL_base = "https://hilgi-docker.herokuapp.com/wiese/baum/"

class Qrcode():
    def __init__(self, baum_nr=0, wiesen_nr=0, wiesen_name="",
                 wiesen_infos=None, geo_infos=None, obst_infos=None,
                 All=False, verbose=0):
        """
            initialisiere die QR-Code Class
        """
        dprint("Qrcode: baum_nr: %s wiesen_nr: %s, wiesen_name: %s" %(
            baum_nr, wiesen_nr, wiesen_name))
        self.baum_nr = baum_nr
        self.wiesen_nr = wiesen_nr
        self.wiesen_name = wiesen_name
        self.geo_infos = geo_infos
        self.wiesen_infos = wiesen_infos
        self.obst_infos = obst_infos
        self.verbose = verbose

        if baum_nr:
            self.baeume = [baum_nr]
        elif wiesen_nr:
            self.baeume = self.get_baueme4wiese(wiesen_nr=wiesen_nr)
        elif wiesen_name:
            self.baeume = self.get_baueme4wiese(wiesen_name=wiesen_name)
        elif All:
            self.baeume = []
            for nr in range(1,16):
                self.baeume += self.get_baueme4wiese(wiesen_nr=nr)

        self.baum_infos = {}

    def get_baueme4wiese(self, wiesen_nr=0, wiesen_name=""):
        """
            gib die passend BaumListe zurück
        """
        if wiesen_nr:
            if not wiesen_nr in self.geo_infos.wiesen_infos:
                print("ERROR: Wiesen Nr could not be found in GEO-Json File")
                sys.exit(3)
            return self.geo_infos.wiesen_infos[wiesen_nr]
        # XXX
        return []

    def get_sorte4baum(self, baum):
        return self.obst_infos.obstsorten[self.geo_infos.baum_infos[int(baum)]['Sorten_id']]['obst_sorte']

    def get_wiesenname4baum(self, baum):
        return self.wiesen_infos.wiesen[self.geo_infos.baum_infos[int(baum)]['Wiesen_Nr']]['name']

    def gen_qr_images(self):
        """
            generiere für dei Bäume in der BaumListe einen QR-Code
        """
        dprint("gen_qr_images")
        for baum in self.baeume:
            dprint("gen_qr_images: %s" % baum)
            url = URL_base + "%s/" % baum
            version, size, img = qrencode.encode_scaled(url, 300)
            if self.verbose:
                print("baum: %s version: %s size: %s" % (
                    baum, version, size ))
            wiese = self.get_wiesenname4baum(baum)
            if not isdir(wiese):
                print("generate Wiesen_dir: '%s'" % wiese)
                makedirs(wiese)
            img_fname = join(wiese, "%s.jpg" % baum)
            img.save(img_fname)
            try:
                self.baum_infos[baum] = {
                    'img' : img_fname,
                    'sorte' : self.get_sorte4baum(baum),
                    'nr'    : baum,
                }
            except:
                # Toter Baum (hat keine Sorte
                pass

class GenPDF():
    def __init__(self, qr_image, pdf_name='/tmp/qr_codes.pdf',
                 page_size='A4', verbose=0):
        """
            generiere für die gegebenen Bäume ein PDF
            das Argument 'qr_image' enthält die Bäume die in dem PDF
            enhalten sein sollen
        """
        self.qr_image = qr_image
        self.verbose = verbose
        self.pdf_name = pdf_name

        self.pdf = FPDF(orientation='L', unit='mm', format=page_size)
        self.pdf.add_page()
        self.pdf.set_line_width(0.0)
        self.pdf.add_font('DejaVu_Sans', '', 'DejaVuSansCondensed-BoldOblique.ttf', uni=True)

        self.pdf.set_font('DejaVu_Sans', '', 24)

        self.act_x = 0
        self.act_y = 0

        self.baum_nr = 0
        if page_size == 'A4':
            self.baum_per_page = 6
            self.baum_per_line = 3
        elif page_size == 'A3':
            self.baum_per_page = 12
            self.baum_per_line = 4

        self.line_h = 100
        self.qr_pic_dim = 90
        self.qr_pic_w = 60


    def draw_rand(self):
        """
            zeichne den Rand um das Bild für den Baum an der act Pos
        """
        # Damit der Rand des letzten Barcodes nicht über den druckbaren
        # Bereich hinaus geht fürgen wir nur beim ersten Schild der
        # Zeile 5mm hizu
        x1 = (self.baum_nr % self.baum_per_line) * self.line_h + \
                    (5 if self.baum_nr % self.baum_per_line == 0 else 0)
        x2 = x1 + self.qr_pic_dim
        if self.baum_nr < self.baum_per_line:
            y1 = self.act_y + 5
            self.act_y = 0
        else:
            y1 = int(self.baum_nr / self.baum_per_line) * self.line_h
            self.act_y = y1
        y2 = y1 + self.qr_pic_dim

        self.pdf.rect(x1, y1, self.qr_pic_dim, self.qr_pic_dim)

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
        x = (self.baum_nr % self.baum_per_line) * self.line_h + \
                    (0 if self.baum_nr % self.baum_per_line == 0 else -5)
        if self.baum_nr < self.baum_per_line:
            y = self.act_y + 7
        else:
            y = self.act_y + 2
        self.pdf.set_xy(x, y)
        self.pdf.cell(w=self.line_h, h=10, align='C', txt="%s" % baum['nr'])

    def draw_sorte(self, baum):
        x = (self.baum_nr % self.baum_per_line) * self.line_h +  \
                    (0 if self.baum_nr % self.baum_per_line == 0 else -5)
        if self.baum_nr < self.baum_per_line:
            y = self.act_y + 10
        else:
            y = self.act_y + 5
        self.pdf.set_xy(x, y)
        self.pdf.cell(w=self.line_h, h=25, align='C',
                      txt=self.get_qr_name(baum['sorte']))

    def draw_image(self, baum):
        x = (self.baum_nr % self.baum_per_line) * self.line_h + 20 + \
                (0 if self.baum_nr % self.baum_per_line == 0 else -5)
        if self.baum_nr < self.baum_per_line:
            y = self.act_y + 30
        else:
            y = self.act_y + 25

        self.pdf.image(baum['img'], x, y,
           w=self.qr_pic_w, h=self.qr_pic_w)

    def add_baum(self, baum):
        """
            zeichne den nächsten Baum
        """
        dprint("add_baum: %s" % pformat(baum))
        if self.verbose:
            print("nr: %s sorte: <%s>" % (baum['nr'], baum['sorte']))
        #
        # Die Positionierung der X-Position muss um den Wert der für
        # den Rand angepasst wurde wiederum hier angepasst werden
        # daher die:
        #       (0 if self.baum_nr % 3 == 0 else -5
        #
        self.draw_rand()
        self.draw_nr(baum)
        self.draw_sorte(baum)
        self.draw_image(baum)


    def gen_pdf(self, ):
        # Sortieren nach Baum Nr. # XXX
        for baum in self.qr_image.baum_infos:
            self.add_baum(self.qr_image.baum_infos[baum])
            self.baum_nr += 1
            if self.baum_nr == self.baum_per_page:
                self.baum_nr = 0
                self.act_y = 0
                self.pdf.add_page()

        self.pdf.output(self.pdf_name)



def usage():
    print( """
USAGE: %(proc)s [-v]  [-f <outfile>] [-p (A4 | A3)] (-b <nr> | --wiese <wiesen-name> | --wiese_nr <nr> | --ALL)
""" % ({ 'proc' : basename(__file__)}))
    sys.exit(err)

if __name__ == '__main__':

    verbose = 0
    baum_nr = 0
    wiesen_nr = 0
    wiesen_name = ""
    outfile = '/tmp/qr_codes.pdf'
    page_size = 'A4'
    AlleWiesen = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vb:f:p:',
                ['wiese=', 'wiese_nr=', 'ALL'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o == '-v':
            verbose += 1
        elif o == '-b':
            baum_nr = a
        elif o == '-f':
            outfile = a
        elif o == '-p':
            page_size = a
            if a not in ('A3', 'A4', 'A5'):
                usage()
        elif o == '--wiese':
            wiesen_name = a
        elif o == '--wiese_nr':
            wiesen_nr = int(a)
        elif o == '--ALL':
            AlleWiesen = True

    wiesen = Wiesen(WiesenFile)

    if wiesen_name:
        if wiesen_name not in wiesen.wiesen_names:
            print("ERROR: unbekannte Wiese '%s'" % wiesen_name)
            if verbose:
                print("""bekannte Wiesen-Namen:
        %s""" % pformat(wiesen.wiesen_names.keys()))
            sys.exit(2)

    elif wiesen_nr:
        if wiesen_nr not in wiesen.wiesen:
            print("ERROR: unbekannte Wiese Nr.'%s'" % wiesen_name)
            if verbose:
                print("""bekannte Wiesen-Nr:
    %s""" % pformat(wiesen.wiesen.keys()))
            sys.exit(2)
    elif AlleWiesen:
        pass
    else:
        if not baum_nr:
            usage()
        # check auf gültigen Baum
        # XXX

    geo_infos = BaumInfos(geo_json_file=BaumJson, verbose=verbose)
    obst_infos = ObstInfos(obst_csv=ObstSorten, verbose=verbose)

    qr = Qrcode(baum_nr=baum_nr,
                wiesen_nr=wiesen_nr,
                wiesen_name=wiesen_name,
                geo_infos = geo_infos,
                wiesen_infos = wiesen,
                obst_infos = obst_infos,
                All = AlleWiesen,
                verbose=verbose)

    qr.gen_qr_images()

    pdf = GenPDF(qr, verbose=verbose, pdf_name=outfile,
                 page_size=page_size)

    pdf.gen_pdf()
