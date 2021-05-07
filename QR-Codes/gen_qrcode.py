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

base_dir = "../init_db"
WiesenFile = join(base_dir, 'wiesen.txt')
BaumJson = join(base_dir, 'Baeume.geojson')
ObstSorten = join(base_dir, 'Obstsorten.csv')

URL_base = "https://hilgi-docker.herokuapp.com/wiese/baum/"

class Qrcode():
    def __init__(self, baum_nr=0, wiesen_nr=0, wiesen_name="",
                 wiesen_infos=None, geo_infos=None, obst_infos=None,
                 verbose=0):
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
            self.baum_infos[baum] = {
                'img' : img_fname,
                'sorte' : self.get_sorte4baum(baum),
                'nr'    : baum,
            }

class GenPDF():
    def __init__(self, qr_image, pdf_name='/tmp/qr_codes.pdf', verbose=0):
        """
            generiere für die gegebenen Bäume ein PDF
            das Argument 'qr_image' enthält die Bäume die in dem PDF
            enhalten sein sollen
        """
        self.qr_image = qr_image
        self.verbose = verbose
        self.pdf_name = pdf_name

        self.pdf = FPDF(orientation='L', unit='mm', format='A4')
        self.pdf.add_page()
        self.pdf.set_line_width(0.0)
        self.pdf.set_font('Arial', 'B', 24)

        self.act_x = 0
        self.act_y = 0

        self.baum_nr = 0
        self.baum_per_page = 6
        self.baum_per_line = 3

        self.line_h = 100
        self.qr_pic_dim = 90
        self.qr_pic_w = 60


    def draw_rand(self):
        """
            zeichne den Rand um das Bild für den Baum an der act Pos
        """
        x1 = (self.baum_nr % self.baum_per_line) * self.line_h + 5
        x2 = x1 + self.qr_pic_dim
        if self.baum_nr < 3:
            y1 = self.act_y + 5
            self.act_y = 0
        else:
            y1 = self.line_h + 5
            self.act_y = self.line_h
        y2 = y1 + self.qr_pic_dim

        self.pdf.rect(x1, y1, self.qr_pic_dim, self.qr_pic_dim)

    def add_baum(self, baum):
        """
            zeichne den nächsten Baum
        """
        dprint("add_baum: %s" % pformat(baum))
        self.draw_rand()
        self.pdf.set_xy((self.baum_nr % self.baum_per_line) * self.line_h,
                        self.act_y + 7)
        self.pdf.cell(w=self.line_h, h=10, align='C', txt="%s" % baum['nr'])
        self.pdf.set_xy((self.baum_nr % self.baum_per_line) * self.line_h,
                        self.act_y + 10)
        self.pdf.cell(w=self.line_h, h=25, align='C', txt=baum['sorte'])
        self.pdf.image(baum['img'],
               x=(self.baum_nr % self.baum_per_line) * self.line_h + 20,
               y=self.act_y + 30,
               w=self.qr_pic_w, h=self.qr_pic_w)

    def gen_pdf(self, ):
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
USAGE: %(proc)s [-v]  (-b <nr> | --wiese <wiesen-name> | --wiese_nr <nr>)
""" % ({ 'proc' : basename(__file__)}))
    sys.exit(err)

if __name__ == '__main__':

    verbose = 0
    baum_nr = 0
    wiesen_nr = 0
    wiesen_name = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vb:',
                ['wiese=', 'wiese_nr='])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o == '-v':
            verbose += 1
        elif o == '-b':
            baum_nr = a
        elif o == '--wiese':
            wiesen_name = a
        elif o == '--wiese_nr':
            wiesen_nr = int(a)

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
                verbose=verbose)

    qr.gen_qr_images()

    pdf = GenPDF(qr, verbose=verbose)

    pdf.gen_pdf()
