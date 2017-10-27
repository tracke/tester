#include <cups/cups.h>
#include <cups/ppd.h>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <map>
#include <cairo/cairo.h>
#include <exception>
#include <math.h>
#include "CairoUtils.h"

using namespace std;

class Error: public exception {
public:
  Error(const string& Message) :
      exception(), Message_(Message) {
  }
  virtual ~Error() throw () {
  }
  virtual const char* what() const throw () {
    return Message_.c_str();
  }
private:
  string Message_;
};

map<string, string> gPaperNames;
typedef pair<string, string> str_pair;

static int GetPrinterResolution(ppd_group_t* group, int num_groups) {
  for (int i = 0; i < num_groups; ++i) {
    ppd_group_t g = group[i];
    for (int j = 0; j < g.num_options; ++j) {
      ppd_option_t o = g.options[j];

      if (!strcmp(o.keyword, "Resolution")) {
        ppd_choice_t c = o.choices[0];

        return atoi(c.choice);
      }
    }
  }

  return 0;
}

static void FindPapersOptions(ppd_option_t& o) {
  if (!strcmp(o.keyword, "PageSize")) {
    for (int i = 0; i < o.num_choices; ++i) {
      ppd_choice_t& c = o.choices[i];

      gPaperNames.insert(str_pair(c.choice, c.text));
    }
  }
}

static void FindPapersGroup(ppd_group_t& g) {
  for (int i = 0; i < g.num_options; ++i)
    FindPapersOptions(g.options[i]);
}

static void FindPapers(ppd_group_t* group, int num_groups) {
  for (int i = 0; i < num_groups; ++i)
    FindPapersGroup(group[i]);
}
/*
 //sample using png file
 void cairo_image(void){
 int              w, h;
 cairo_surface_t *image;

 image = cairo_image_surface_create_from_png ("data/romedalen.png");
 w = cairo_image_surface_get_width (image);
 h = cairo_image_surface_get_height (image);

 cairo_translate (cr, 128.0, 128.0);
 }
 */
void CreateLabelImage(int Width, int Height, int LabelPos, char *data[], string&Barcode, string& FileName) {
//  const char* PNGFileName = "label.png";
  FileName = "label.png";
  double x, y = 0;
  double image_start = 0;
  int  image_width, label_height;

  CairoSurfacePtr Surface(cairo_image_surface_create(CAIRO_FORMAT_RGB24, Width, Height));
  if (!*Surface)
    throw Error("Unable to create cairo surface");

  CairoPtr c(cairo_create(Surface));
  if (!*c)
    throw Error("Unable to create cairo_t");

  // setup cairo
  cairo_set_antialias(c, CAIRO_ANTIALIAS_NONE);

  //set up label position
  double CanvasWidth = (Width / 2.25);
  double y_offset = 0;
  double x_offset = 0;

  // there seems to be a margin for label position 1 that isn't there for label position 2
  if (LabelPos == 2) {
    x_offset = Width/1.75;
  }

  cairo_surface_set_device_offset(Surface, x_offset, y_offset);

  // clear image
  cairo_set_source_rgb(c, 1, 1, 1);
  cairo_paint(c);
  cairo_save(c);

  cairo_set_source_rgb(c, 0, 0, 0);
  cairo_set_line_width(c, 5);

// load an image from the file
  CairoSurfacePtr Image(cairo_image_surface_create_from_png(Barcode.c_str()));
  if (!*Image)
    throw Error("Unable to load image file");
  CairoPtr im(cairo_create(Image));
  if (!*im)
    throw Error("Unable to create cairo_t");

 // text_start = cairo_image_surface_get_height(Image);
  image_width = cairo_image_surface_get_width(Image);
//  label_height = cairo_image_surface_get_height(Surface);
  image_start = (CanvasWidth - image_width) / 2;

  cairo_set_source_surface(c, Image, image_start, 3);
  cairo_paint(c);
  cairo_restore(c);
  cairo_save(c);

  printf("Printing %d  image on a %f canvas starting at %f\r\n",image_width, CanvasWidth, x_offset);


  // set up font
  cairo_select_font_face(c, "courier", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_BOLD);
  cairo_set_font_size(c, 10);
  cairo_set_source_rgb(c, 0, 0, 0);
  cairo_set_line_width(c, 1);

  // calculate how big the chars can be based off of 1st line
  cairo_text_extents_t te;
  for (int FontSize = 100;; FontSize -= 1){ //change from '-=10' to '-=1'
    cairo_set_font_size(c, FontSize);
    cairo_text_extents(c, data[0], &te);
    if ((CanvasWidth - 6) > te.width)
      break;
  }

//and print text, starting at the bottom of the label
  y = (double) Height - te.height;
  for (int i = 0; i < 3; ++i) {
    x = (CanvasWidth - te.width) / 2;
    cairo_move_to(c, x, y);
    cairo_show_text(c, data[2 - i]);
    cairo_stroke(c);
    y -= te.height * 2;
  }

  // save to file
  const char * PNGFileName = FileName.c_str();

  if (cairo_surface_write_to_png(Surface, PNGFileName) != CAIRO_STATUS_SUCCESS)
    throw Error("Unable to write to PNG file");
}


/********************************************************************************
 *   main to be called with following arguments:
 *    Printer name:
 *    Label type ( currently 30333 1/2" x 1", 2 up label)
 *    Label position: for 2 up labels. Left label is '1' and right label is '2'
 *    File name: name of datamatrix in png format (default=uut.png)
 *    Line 1: XXX.Y-WWW        where X=Product code, Y=version, W = work order
 *    Line 2: 00 00 00              first 3 bytes of HWID
 *    Line 3: 00 00 00              remaining 3 bytes of hwid
 *
 ********************************************************************************
 */
int main(int argc, char** argv) {
  try {
    if (argc < 7)
      throw Error("Usage: PrintLabel <PrinterName> <LabelType><[Label (1 or 2)><barcode file><Line 1><Line 2><Line 3>");

    int LabelPos;
    char *data[3];

    const char* ppdFileName = cupsGetPPD(argv[1]);

    if (!ppdFileName)
      throw Error(string("Unknown printer '") + argv[1] + "'");

    ppd_file_t* ppd = ppdOpenFile(ppdFileName);
    if (!ppd)
      throw Error(string("Unable to open ppd file '") + ppdFileName + "'");

    FindPapers(ppd->groups, ppd->num_groups);
    int Resolution = GetPrinterResolution(ppd->groups, ppd->num_groups);

    for (int i = 0; i < ppd->num_sizes; ++i) {
      ppd_size_t size = ppd->sizes[i];
      if (argc >= 3)
        if (argv[2] != gPaperNames[size.name].substr(0, 5))
          continue;

// Determine Label position.If not 1 or 2 then leave Label position at 1
      LabelPos = atoi(argv[3]);
      if (LabelPos != 1 &&  LabelPos != 2) {
          LabelPos=1;
      }

// Get datamatrix image
      string BarcodeFile = argv[4];

//Load up lines to be printed
      data[0]=argv[5];
      data[1]=argv[6];
      data[2]=argv[7];

/***************** USED FOR DEBUG **********************
      printf("Printing %s %s %s ",data[0],data[1],data[2]);
      printf("and image from %s",BarcodeFile.c_str());
      printf(" to Label at Position %d\r\n", LabelPos);

      printf("Please Insert '%s' paper. Press 'c' to continue, 's' to skip: ", gPaperNames[size.name].c_str());
      while ((ch = getchar()) == '\n') {
      }
      if (ch == 's')
        continue;
      if (ch == 'a')
        break;
********************************************************
*/
      int Width = int((size.right - size.left) * Resolution / 72);
      int Height = int((size.top - size.bottom) * Resolution / 72);
      bool Landscape = false;

      printf("Label:w%3.2f'h%3.2f'\r\n", size.width, size.length);
      printf("image size(pxl):w%dh%d\r\n", Width, Height);

      string FileName;
      /*
       if (Height > Width)
       {
       Landscape = true;
       int t = Width;
       Width = Height;
       Height = t;
       }
       */

      CreateLabelImage(Width, Height, LabelPos, data, BarcodeFile, FileName);

      int num_options = 0;
      cups_option_t* options = NULL;

      num_options = cupsAddOption("PageSize", size.name, num_options, &options);
      num_options = cupsAddOption("scaling", "100", num_options, &options);
      if (Landscape)
        num_options = cupsAddOption("landscape", "no", num_options, &options);
      //num_options = cupsAddOption("orientation-requested", "4", num_options, &options);

      cupsPrintFile(argv[1], FileName.c_str(), "Printing Barcode", num_options, options);

      cupsFreeOptions(num_options, options);
    }

    ppdClose(ppd);

    return 0;
  } catch (std::exception& e) {
    fprintf(stderr, e.what());
    fprintf(stderr, "\n");
    return 1;
  }
}
