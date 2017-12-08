#!/usr/bin/env python
# encoding: utf-8

# Filename    : ftn2c.py
# Description : Converts bitmap font(s) generated by BMFont to C code
# Author      : Lars Ole Pontoppidan, 2014, Modified by Gabor Kiss-Vamosi for LittelvGL, 2017
# URL         : http://larsee.dk/, http://www.gl.littlev.hu

script_revision = '2017-09-24'

# --------------------------------  LICENSE  -----------------------------------
#
# Copyright (c) 2014, Lars Ole Pontoppidan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# *  Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# *  Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# *  Neither the name of the original author (Lars Ole Pontoppidan) nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# --------------------------------  README  ------------------------------------
#
# fnt2c.py reads bitmap font output from the Bitmap Font Generator by
# AngelCode: http://www.angelcode.com/products/bmfont/  and outputs byte table 
# arrays in C language which is compatible with LittlevGL fonts
#
# In BMFont set the following:
#   - Options/Export settings:
#      - Width and Height: 2048
#      - Font descriptor: XML
#      - Texture: png
# 
#Usage
#  python fnt2c.py -f <font_name> [-o <output file> -s <start unicode> -e <end unicide> -i]
#
# Options
#   -f, --font    name of the font file without any extension (e.g. arial_10)
#   -o, --output  name of the output file without any extension (e.g. arial_10_cyrillic).   Optional, default: font name
#   -s, --start   first unicode charater to convert (e.g. 1024).                            Optional, default: 32
#   -e, --end     last unicode charater to convert (e.g. 1279).                             Optional, default: 126
#   -i  --autoinc start adress of ato increment                                             Optional, default: OFF
# Example
#  Convert the ASCII characters from dejavu_20.fnt/png and save to devaju_20.c/h         
#    python fnt2c.py -f dejavu_20    
#    
#  Convert the Cyrillic code page from dejavu_20.fnt/png and save to devaju_20_cyrillic.c/h
#    python fnt2c.py -f dejavu_20 -o dejavu_20_cyrillic -s 1024 -e 1279

from PIL import Image as image
from xml.dom import minidom
import sys, getopt, os.path

class Config:
    def __init__(self, argv):       

        self.font  = ""
        self.input_file  = ""
        self.output_file  = ""
        self.height = 0
        
        # Ascii range to grab
        self.first_unicode  = 32
        self.last_unicode   = 126
        self.autoinc = -1
        self.sys = 0
        self.glyph_cnt = 0
        
        try:
            opts, args = getopt.getopt(argv, "f:o:s:e:i:h",["font=","output=","start=","end=","help", "autoinc", "sys"])
        except getopt.GetoptError:
            print 'Usage: python fnt2c.py -f <font_name> [-o <output file> -s <start unicode> -e <end unicide> -i <auto inc. start>]' 
            sys.exit(2)
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print 'Usage' 
                print '  python fnt2c.py -f <font_name> [-o <output file> -s <start unicode> -e <end unicide>  -i <auto inc. start> --sys]\n'
                print 'Options' 
                print '  -f, --font    name of the font file without any extension (e.g. arial_10)'
                print '  -o, --output  name of the output file without any extension (e.g. arial_10_cyrillic).   Optional, default: font name '
                print '  -s, --start   first unicode charater to convert (e.g. 1024).                            Optional, default: 32'
                print '  -e, --end     last unicode charater to convert (e.g. 1279).                             Optional, default: 126\n'
                print '  -i  --autoinc start adress of auto increment                                             Optional, default: OFF'
                print '  --sys         create as built in font (to be enabled in lv_conf.h and strored in lv_misc/lv_fonts/)'
                print 'Example' 
                print '  Convert the ASCII characters from dejavu_20.fnt/png and save to devaju_20.c/h'              
                print '    python fnt2c.py -f dejavu_20\n'
                print '  Convert the Cyrillic code page from dejavu_20.fnt/png and save to devaju_20_cyrillic.c/h'
                print '    python fnt2c.py -f dejavu_20 -o dejavu_20_cyrillic -s 1024 -e 1279'
                sys.exit()
            elif opt in ("-f", "--font"):
                self.font = arg
            elif opt in ("-o", "--output"):
                self.output_file = arg
            elif opt in ("-s", "--start"):
                self.first_unicode = int(arg)
            elif opt in ("-e", "--end"):
                self.last_unicode = int(arg)
            elif opt in ("-i", "--autoinc"):
                self.autoinc = int(arg)
            elif opt in ("--sys"):
                self.sys = 1

        if self.font == "":
            print "ERROR: No font specified"
            print "       Usage: -f <font_name>[-o <output file> -s <start unicode> -e <end unicide>  -i <auto inc. start> --sys]" 
            sys.exit()
        
        
        self.input_file = self.font + ".fnt"
        if(self.output_file == ""): self.output_file = self.font        
        
def makeFontStyleDecl(config):
    if config.sys :
        s = "\nlv_font_t lv_font_%s = \n" % config.output_file
    else :
        s = "\nlv_font_t font_%s = \n" % config.output_file
    s += "{\n"
    if config.autoinc >= 0:
        if config.autoinc == 57344:  #basic symbols defined for non UTF-8 usage too
            s += "#if LV_TXT_UTF8 == 0\n"
            s += "    192,        /*First letter's unicode */\n" 
            s += "    207,        /*Last letter's unicode */\n" 
            s += "#else\n"
            s += "    %d,        /*First letter's unicode */\n" % config.autoinc
            s += "    %d,        /*Last letter's unicode */\n" % (config.autoinc + config.glyph_cnt) 
            s += "#endif\n"
            
        elif config.autoinc == 57408:  #feedback symbols defined for non UTF-8 usage too
            s += "#if LV_TXT_UTF8 == 0\n"
            s += "    208,        /*First letter's unicode */\n" 
            s += "    223,        /*Last letter's unicode */\n" 
            s += "#else\n"
            s += "    %d,        /*First letter's unicode */\n" % config.autoinc
            s += "    %d,        /*Last letter's unicode */\n" % (config.autoinc + config.glyph_cnt) 
            s += "#endif\n"
            
        elif config.autoinc == 57376:  #file symbols defined for non UTF-8 usage too
            s += "#if LV_TXT_UTF8 == 0\n"
            s += "    224,        /*First letter's unicode */\n" 
            s += "    255,        /*Last letter's unicode */\n" 
            s += "#else\n"
            s += "    %d,        /*First letter's unicode */\n" % config.autoinc
            s += "    %d,        /*Last letter's unicode */\n" % (config.autoinc + config.glyph_cnt) 
            s += "#endif\n"
        else:
            s += "    %d,        /*First letter's unicode */\n" % config.autoinc
            s += "    %d,        /*Last letter's unicode */\n" % (config.autoinc + config.glyph_cnt) 
    else: 
        s += "    %d,        /*First letter's unicode */\n" % (config.first_unicode)
        s += "    %d,        /*Last letter's unicode */\n" % config.last_unicode
    
    s += "    %d,        /*Letters height (rows) */\n" % config.height
    s += "    %s_bitmap,    /*Glyph's bitmap*/\n" % config.output_file
    s += "    %s_map,    /*Glyph start indexes in the bitmap*/\n" % config.output_file
    s += "    %s_width,    /*Glyph widths (columns)*/\n" % config.output_file
    s += "    NULL         /*No next page by default*/\n"
    s += "};\n\n"
    if(config.sys):
      s += "#endif /*USE_LV_FONT_" + config.output_file.upper() +"*/\n"
    return s
    
    
def makeBitmapsTable(config, img, glyphs):

    s = "/*Store the image of the letters (glyph) */\nstatic const uint8_t %s_bitmap[] = \n{" % (config.output_file)
    autoinc_tmp = config.autoinc
    
    
    for ascii in range(config.first_unicode, config.last_unicode + 1):        
        
        # Find the glyph
        glyph_found = None
        for glyph in glyphs:
            if glyph.id == ascii:
                glyph_found = glyph
                break
            
        if glyph_found is None:
            if config.autoinc >= 0: 
                continue
            print("INFO: No glyph for U+%s, using substitute" % hex(ascii).split('x')[-1]) 
            s += "\n    // No glyph for U+%s, using substitute" % hex(ascii).split('x')[-1]
            # We use first glyph instead
            glyph_found = glyphs[0]
            
            
        if config.autoinc >= 0:
            glyph_found.id = autoinc_tmp
            autoinc_tmp = autoinc_tmp + 1
        s += glyph_found.makeBitmapCode(img, config.height)
                    
                    
        if config.autoinc >= 0:
            glyph_found.id = ascii  #Restore ID
    s += "};\n"
    
    config.glyph_cnt = autoinc_tmp - config.autoinc;
    
    return s
    
        
def makeWidthsTable(config, glyphs):
    width_map_s = "/*Store the width (column count) of each glyph*/\nstatic const uint8_t %s_width[] = \n{" % (config.output_file)
    i = 0
    
    for ascii in range(config.first_unicode, config.last_unicode + 1):        
        # Find the glyph
        glyph_found = None
        for glyph in glyphs:
            if glyph.id == ascii:
                glyph_found = glyph
                break
            
        if glyph_found is None:
            if config.autoinc >= 0: 
                continue
            # We use first glyph instead
            glyph_found = glyphs[0]
                        
        if i == 0:                    
            width_map_s += "\n    "
        
        i = (i + 1) % 8 
        
        width_map_s += '%2d, ' % (glyph_found.xadvance)

            
    width_map_s += "\n};\n"
    return width_map_s

def makeMapTable(config, glyphs):
    font_map_s = "/*Store the start index of the glyphs in the bitmap array*/\nstatic const uint32_t %s_map[] = \n{" % (config.output_file)
    i = 0
    w_act = 0
    
    for ascii in range(config.first_unicode, config.last_unicode + 1):        
        # Find the glyph
        glyph_found = None
        for glyph in glyphs:
            if glyph.id == ascii:
                glyph_found = glyph
                break
            
        if glyph_found is None:
            if config.autoinc >= 0: 
                continue
            # We use first glyph instead
            glyph_found = glyphs[0]
                        
        if i == 0:                    
            font_map_s += "\n    "    
        
        i = (i + 1) % 8 
        w_tmp = glyph_found.xadvance / 8
        if(glyph_found.xadvance % 8): w_tmp += 1
        w_tmp *= config.height
        font_map_s += '%2d, ' % (w_act)

        w_act += w_tmp                            
            
    font_map_s += "\n};\n"
    return font_map_s
    
    
def loadFont(config):    
    # Open xml
    if not os.path.isfile(config.input_file): 
        print "ERROR: " + config.input_file + " not exists"
        sys.exit()
          
    print("Reading font description: " + config.input_file)
    font = minidom.parse(config.input_file)

    config.height = font.getElementsByTagName('info')[0].attributes['size'].value
    config.height = int(config.height)
    
    # Open page 0 image:
    file_img = font.getElementsByTagName('page')[0].attributes['file'].value
    
    if not os.path.isfile(file_img): 
        print "ERROR: " + file_img + " not exists"
        sys.exit()
        
    print("Reading font bitmap: " + file_img)
    img = image.open(file_img)
    
    print "SETTINGS"
    print "Font: %s" % config.font
    print "Output: %s" % config.output_file
    print "Heght: %s" % config.height
    print "First unicode: %s" % config.first_unicode
    print "Last unicode: %s" % config.last_unicode
    if config.autoinc >= 0: print "Auto increment start: %s" % config.autoinc
    else: print "Auto increment: OFF" 
    print "-----------------"
    
    
    # Get the glyphs
    chars = font.getElementsByTagName('char')
    
    glyphs = []
    for char in chars:
        glyphs.append(Glyph(char))
        
    return (img, glyphs)
    
def makeFontSource(config):
    img, glyphs = loadFont(config)
    
    source =  "\n" + makeBitmapsTable(config, img, glyphs) + "\n"
    
    source += makeMapTable(config, glyphs) + "\n"
    
    source += makeWidthsTable(config, glyphs)
    
    source += makeFontStyleDecl(config)

    return source
 
def processConfig(conf):
    # Get the general configuration
    output_header = conf.output_file + ".h"
    output_source = conf.output_file + ".c"
    
    # Start up the header and source file
    header = "#ifndef " + conf.output_file.upper() + "_H\n"
    header += "#define " + conf.output_file.upper() + "_H\n\n"  
    header += "/*Use UTF-8 encoding in the IDE*/\n\n"
    if(conf.sys):
      header += '#include "../../../lv_conf.h"\n'
      header += "#if USE_LV_FONT_" + conf.output_file.upper() + "\n\n"
      header += '#include <stdint.h>\n#include "../lv_font.h"\n\n'
    else:
      header += '#include <stdint.h>\n#include "lvgl/lv_misc/lv_font.h"\n\n'
    if(conf.sys):
      header += "extern lv_font_t lv_font_%s;\n\n" % conf.output_file
    else:
      header += "extern lv_font_t font_%s;\n\n" % conf.output_file

    if(conf.sys):
      header += "#endif /*USE_LV_FONT_" + conf.output_file.upper() +"*/\n"
    header += "#endif   /*%s_H*/" % conf.output_file.upper()

    source = "";        
    if(conf.sys):
      source += '#include "../../../lv_conf.h"\n'
      source += "#if USE_LV_FONT_" + conf.output_file.upper() + "\n\n"
      source += '#include <stdint.h>\n#include "../lv_font.h"\n'
    else :
      source += '#include <stdint.h>\n#include "lvgl/lv_misc/lv_font.h"\n\n'
           

    source += makeFontSource(conf);
    
    print("Writing output: " + output_source) 
    with open(output_source, "w") as text_file:
        text_file.write(source)
        
    print("Writing output: " + output_header)
    with open(output_header, "w") as text_file:
        text_file.write(header)


class Glyph:
    def __init__(self, char):
        self.id = int(char.attributes['id'].value)
        self.x  = int(char.attributes['x'].value)
        self.y  = int(char.attributes['y'].value)
        self.width = int(char.attributes['width'].value)
        self.height = int(char.attributes['height'].value)        
        self.xoffset  = int(char.attributes['xoffset'].value)
        self.yoffset  = int(char.attributes['yoffset'].value)       
        self.xadvance = int(char.attributes['xadvance'].value)
        
    def makeBitmapCode(self, img, height):
        s = '\n    // ASCII: %d, char width: %d' % (self.id, self.xadvance)
        width = (self.xadvance / 8) * 8
        if(self.xadvance % 8): width = width + 8;

        for y in range(0, height):
            comment = ""
            bytestring = ""
            byte = 0
            mask = 128
 
            for x in range(0, width):
                use_x = x - self.xoffset
                use_y = y - self.yoffset
                pixel = 0
                if (use_x >= 0) and (use_x < self.width) and (use_y >= 0) and (use_y < self.height):
                    if img.getpixel((use_x + self.x, use_y + self.y)) > 127:
                        pixel = 1
                        
                if pixel != 0:
                    comment += 'O'
                    byte |= mask
                else:
                    if x >= self.xadvance:
                        comment += '.'
                    else:
                        comment += '-'
                
                mask = mask // 2
                
                if mask == 0:
                    bytestring += "0x%02x, " % byte
                    mask = 128
                    byte = 0
                    
            if mask != 128:
                bytestring += "0x%02x, " % byte
            
            s += "\n    " + bytestring + " // " + comment
            
        return s + "\n"
       
def main(argv):
    print "-----------------"
    print("Font converter for LittlevGL (BMFont .fnt -> .c .h)\nVersion: %s (based on Lars Ole Pontoppidan's script)" % script_revision)
    print "-----------------"
    conf = Config(argv)
    processConfig(conf)
    print "-----------------\nRAEDY!"

if __name__ == "__main__":
    main(sys.argv[1:])    
   
    
