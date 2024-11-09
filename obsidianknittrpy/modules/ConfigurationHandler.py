import yaml
import os
import argparse


class ConfigurationHandler:

    def __init__(self, last_run_path=None):
        """Initialises the default settings"""
        # Load default configuration in code
        self.init_default_settings()  # not exported, not saved
        self.init_default_pipeline()  # not exported, not saved
        self.init_default_format_definitions()  # not exported, not saved
        self.file_history = []
        self.last_run_path = None
        ## initiate the applied settings instanes by copying over the default settings
        if last_run_path is not None and os.path.exists(last_run_path):
            self.last_run_path = last_run_path

    def apply_defaults(self):
        """Apply the default settings to the applied settings"""
        self.applied_settings = self.load_default_settings()
        self.applied_pipeline = self.load_default_pipeline()
        self.applied_format_definitons = self.load_default_format_definitions()

    def init_default_settings(self):
        self.default_settings = {
            "DIRECTORIES_PATHS": {
                "app_dir": "/path/to/app",
                "work_dir": "/path/to/work",  # default equals app_dir
                "output_dir": "/path/to/output",  # default equals app_dir
                "own_ohtml_fork_dir": None,  # Must be set if `use_custom_fork` is true
            },
            "OBSIDIAN_HTML": {
                "verb": True,
                "use_custom_fork": False,
                "purge_errors": False,
                "verbose_flag": False,
                "limit_scope": False,
            },
            "GENERAL_CONFIGURATION": {
                "remove_hashtags_from_tags": False,
                "strip_local_md_links": False,
                "keep_filename": False,
                "render_to_outputs": False,
                "backup_output_before_rendering": False,
            },
            "ENGINE_SPECIFIC_STUFF": {"quarto_strip_reference_prefixes": False},
            "EXECUTION_DIRECTORIES": {"exec_dir_selection": 1},
        }

    def init_default_pipeline(self):
        self.default_pipeline_yaml = """
pipeline:
  - file_name: convert_obsidianhtml_image_srcs
    module_name: ConvertImageSRCs
    config: {}
    enabled: True
  - file_name: general_processing
    module_name: ProcessTags
    config: {remove_hashtags_from_tags: False, obsidian_tag_end_chars: []}
    enabled: True
  - file_name: general_processing
    module_name: ProcessAbstract
    config: {}
    enabled: False
  - file_name: convert_diagrams
    module_name: ProcessDiagramCodeblocks
    config: {codeblock_langs: ["mermaid","dot"]}
    enabled: True
  - file_name: general_processing
    module_name: ProcessFrontmatterNulls
    config: {}
    enabled: True
  - file_name: quarto_modules
    module_name: ProcessInvalidQuartoFrontmatterFields
    config: {erroneous_keys: {"aliases":[]}}
    enabled: True
  - file_name: module_file
    module_name: ModuleName
    config: {}
    enabled: True
"""

    def init_default_format_definitions(self):
        self.default_format_definitions = """
;PACKAGE::FORMAT
	;Key:Control|Type|Default|String|Tab3Parent|Value|Other
	;Disable a package by prepending a ";" on the non-indented line at the start of the package definition.

quarto::html
	number-depth:edit|Type:Integer|Default:3|String:"What is the maximum depth of sections that should be numbered?"|Max:99|Min:1|ctrlOptions:Number|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/output-formats/html-basics.html#section-numbering"|Linktext:?
	number-sections:checkbox|Type:boolean|Default:1|String:"Do you want to number your sections automatically?"|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/output-formats/html-basics.html#section-numbering"|Linktext:?
	toc:checkbox|Type:boolean|Default:1|String:"Do you want to include a ToC?"|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/output-formats/html-basics.html#table-of-contents"|Linktext:?
	toc-depth:edit|Type:Integer|Default:3|String:"What is the maximum depth the ToC should display?"|Max:5|Min:1|ctrlOptions:Number|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/output-formats/html-basics.html#table-of-contents"|Linktext:?
	; toc-expand
	toc-location:ddl|Type:String|Default:"left"|String:"Select ToC Location"|ctrlOptions:body,left,right|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/output-formats/html-basics.html#table-of-contents"|Linktext:?
	toc-title:edit|Type:String|String:"Set the ToC's Title"|Default:"Table of Contents"|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/output-formats/html-basics.html#table-of-contents"|Linktext:?
	df-print:ddl|Type:String|Default:"kable"|String:"Choose Method for printing data frames"|ctrlOptions:default,kable,tibble,paged|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/html.html#tables"|Linktext:?
	;TODO: Finish this format, modify DynamicArguments.ahk to accept lists via a parameters "Tab3Parent" relationship: so we can map which kinds of string format we need for each package.
	fig-width:edit|Type:Integer|Default:8|String:"Set default width in inches for figures"|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/html.html#figures"|Linktext:?
	fig-height:edit|Type:Integer|Default:6|String:"Set default height in inches for figures"|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/html.html#figures"|Linktext:?
	fig-cap-location:ddl|Type:String|Default:margin|String:"Select location of figure caption"|ctrlOptions:Top,Bottom,Margin|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/html.html#figures"|Linktext:?
	tbl-cap-location:ddl|Type:String|Default:margin|String:"Select location of table caption"|ctrlOptions:Top,Bottom,Margin|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/html.html#tables"|Linktext:?
	fig-title:combobox|Type:String|Default:Figure|String:"Specify title prefix on figure-captions"|ctrlOptions:Figure,Fig.|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/html.html#figures"|Linktext:?
	fig-responsive:checkbox|Type:boolean|Default:1|String:"Do you want to make images responsive?"|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/html.html#figures"|Linktext:?
	email-obfuscation:ddl|Type:String|Default:none|String:"Specify a method for obfuscating 'mailto'-links in HTML documents"|ctrlOptions:none,javascript,references|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/formats/html.html#format-options"|Linktext:?
	reference-location:ddl|Type:String|Default:margin|String:"Set reference position"|ctrlOptions:bottom,margin|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/formats/html.html#footnotes"|Linktext:?
	citation-location:ddl|Type:String|Default:margin|String:"Set citation position"|ctrlOptions:bottom,margin|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/formats/html.html#references"|Linktext:?
	citations-hover:checkbox|Type:boolean|Default:1|String:"Enables a hover popup for citations that shows the reference information"|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/output-formats/html-basics.html#reference-popups"|Linktext:?
	footnotes-hover:checkbox|Type:boolean|Default:1|String:"Enables a hover popup for footnotes that shows the footnote contents"|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/output-formats/html-basics.html#reference-popups"|Linktext:?
	code-fold:ddl|Type:String|Default:true|String:"Collapse code into HTML <details> tag so the user can display it on-demand"|ctrlOptions:true,false,show|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/output-formats/html-code.html#folding-code"|Linktext:?
	date:combobox|Type:String|Default:now|String:"Specify dynamic date to use when compiling"|ctrlOptions:today,now,last-modified|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/formats/html.html#title-author"|Linktext:?
	date-format:combobox|Type:String|Default:DD.MM.YYYY|String:"Specify date format to use when compiling"|ctrlOptions:iso,full,long,medium,short,DD.MM.YYYY|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/dates.html"|Linktext:?
	;standalone:checkbox|Type:boolean|Default:1|String:"Produce output with an appropriate header and footer, aka not a fragment"|ctrlOptions:disabled|Tab3Parent:3. Misc
	code-overflow:ddl|Type:String|Default:Scroll|String:|ctrlOptions:Scroll,Wrap|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/output-formats/html-code.html#code-overflow"|Linktext:?
	embed-resources:checkbox|Type:boolean|Default:1|String:"Produce a standalone HTML file with no external dependencies using 'data:'-URIs"|ctrlOptions:disabled|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/formats/html.html#rendering"|Linktext:?
	link-external-icon:checkbox|Type:boolean|Default:0|String:"Show a special icon next to links that leave the current site"|Tab3Parent:4. Links|Link:"https://quarto.org/docs/reference/formats/html.html#links"|Linktext:?
	link-external-newwindow:checkbox|Type:boolean|Default:1|String:"Open external links in a new browser window/tab (don't navigate the current tab)"|Tab3Parent:4. Links|Link:"https://quarto.org/docs/reference/formats/html.html#links"|Linktext:?
	author:combobox|Type:String|Default:"Gewerd Strauss"|String:"Set Author for this output format"|ctrlOptions:Author1,Gewerd Strauss,redacted|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/formats/html.hftml#title-author"|Linktext:?
	filesuffix:Meta|Value:html
	inputsuffix:Meta|Value:qmd
	renderingpackage_start:Meta|Value:quarto::quarto_render("index.qmd",execute_params = list(
	renderingpackage_end:Meta|Value:),output_format = "html","%name%.html")
	dateformat:Meta|Value:{A_DD}.{A_MM}.{A_YYYY}
	package:Meta|Value:quarto

quarto::docx
	number-depth:edit|Type:Integer|Default:3|String:"What is the maximum depth of sections that should be numbered?"|Max:99|Min:1|ctrlOptions:Number|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/reference/formats/docx.html#numbering"|Linktext:?
	number-sections:checkbox|Type:boolean|Default:1|String:"Do you want to number your sections automatically?"|Tab3Parent:1. ToC and Numbering|Value:0|Link:"https://quarto.org/docs/reference/formats/docx.html#numbering"|Linktext:?
	toc:checkbox|Type:boolean|Default:0|String:"Do you want to include a ToC?"|Tab3Parent:1. ToC and Numbering|Value:0|Link:"https://quarto.org/docs/reference/formats/docx.html#table-of-contents"|Linktext:?
	toc-depth:edit|Type:Integer|Default:3|String:"What is the maximum depth the ToC should display?"|Max:5|Min:1|ctrlOptions:Number|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/reference/formats/docx.html#table-of-contents"|Linktext:?
	;number-offset:edit|Type:String|Default:0|String:"Offset for section headings in output?"|Tab3Parent:1. ToC and Numbering|Value:0|Link:"https://quarto.org/docs/reference/formats/docx.html#numbering"|Linktext:?
	toc-title:edit|Type:String|String:"Set the ToC's Title"|Default:"Table of Contents"|Tab3Parent:1. ToC and Numbering|Link:"https://quarto.org/docs/reference/formats/docx.html#table-of-contents"|Linktext:?
	reference-doc:file|Type:String|Default:"BE28 Template Internship Report - Kopie.docx"|String:"Choose format-reference Word-file."|SearchPath:""|Tab3Parent:3. General|Link:"https://quarto.org/docs/reference/formats/docx.html#format-options"|Linktext:?
	df-print:ddl|Type:String|Default:"kable"|String:"Choose Method for printing data frames"|ctrlOptions:default,kable,tibble,paged|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/docx.html#tables"|Linktext:?
	;TODO: Finish this format, modify DynamicArguments.ahk to accept lists via a parameters "Tab3Parent" relationship: so we can map which kinds of string format we need for each package.
	fig-height:edit|Type:Integer|Default:6|String:"Set default height in inches for figures"|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/docx.html#figures"|Linktext:?
	fig-width:edit|Type:Integer|Default:8|String:"Set default width in inches for figures"|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/docx.html#figures"|Linktext:?
	;out-width:edit|Type:Integer|Default:8|String:"Set default width in inches for figure containers"|Tab3Parent:2. Figures and Tables
	;fig-asp:edit|Type:Number|Default
	fig-dpi:edit|Type:Integer|Default:96|String:"Set figure dpi"|ctrlOptions:Number|Tab3Parent:2. Figures and Tables|Link:"https://quarto.org/docs/reference/formats/docx.html#figures"|Linktext:?
	date:combobox|Type:String|Default:now|String:"Specify dynamic date to use when compiling"|ctrlOptions:today,now,last-modified|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/dates.html"|Linktext:?
	date-format:combobox|Type:String|Default:DD.MM.YYYY|String:"Specify date format to use when compiling"|ctrlOptions:iso,full,long,medium,short,DD.MM.YYYY|Tab3Parent:3. Misc|Link:"https://quarto.org/docs/reference/dates.html"|Linktext:?
	author:combobox|Type:String|Default:"Author 1"|String:"Set Author for this output format"|ctrlOptions:Author 1,Gewerd Strauss,redacted|Tab3Parent:3. General|Link:"https://quarto.org/docs/reference/formats/docx.html#title-author"|Linktext:?
	renderingpackage_start:Meta|Value:quarto::quarto_render("index.qmd",execute_params = list(
	renderingpackage_end:Meta|Value:),output_format = "docx","%name%.docx")
	filesuffix:Meta|Value:docx
	inputsuffix:Meta|Value:qmd
	dateformat:Meta|Value:{A_DD}.{A_MM}.{A_YYYY}
	package:Meta|Value:quarto

quarto::pdf
	; Title & Author
	; title:edit|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	; subtitle:edit|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	; date:edit|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	; author:edit|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	; abstract:edit|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	date:combobox|Type:String|Default:now|String:"Specify dynamic date to use when compiling"|ctrlOptions:today,now,last-modified|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/dates.html"|Linktext:?
	date-format:combobox|Type:String|Default:DD.MM.YYYY|String:"Specify date format to use when compiling"|ctrlOptions:iso,full,long,medium,short,DD.MM.YYYY|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/dates.html"|Linktext:?
	author:combobox|Type:String|Default:"Author1"|String:"Set Author for this output format"|ctrlOptions:Author1,Gewerd Strauss,redacted|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	thanks:edit|Type:String|Default:""|String:"The contents of an acknowledgments footnote after the document title"|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	; ;order:edit|Tab3Parent:Title & Author|Link:"https://quarto.org/docs/reference/formats/pdf.html#title-author"|Linktext:?
	; ; Format Options
	pdf-engine:combobox|Type:String|Default:xelatex|String:"Use specified pdf engine. Give full path if engine not on PATH. Do not use 'pdflatex' if you have unicode-characters"|ctrlOptions:xelatex,pdflatex,lualatex,tectonic,latexmk,context,wkhtmltopdf,prince,weasyprint,pdfroff|Tab3Parent:Format options|Link:"https://quarto.org/docs/reference/formats/pdf.html#format-options"|Linktext:?
	pdf-engine-opt:edit|Type:String|Default:"[]"|String:"Give command-line argument to the pdf-engine"|Tab3Parent:Format options|Link:"https://quarto.org/docs/reference/formats/pdf.html#format-options"|Linktext:?
	; ; Table of contents
	toc:checkbox|Type:boolean|Default:1|String:"Include an automatically generated ToC"|Tab3Parent:Table of Contents|Link:"https://quarto.org/docs/reference/formats/pdf.html#table-of-contents"|Linktext:?
	toc-depth:edit|Type:integer|Default:3|String:"Specify the number of section levels to include in the ToC"|Max:5|Min:1|ctrlOptions:Number|Tab3Parent:Table of Contents|Link:"https://quarto.org/docs/reference/formats/pdf.html#table-of-contents"|Linktext:?
	toc-title:edit|Type:String|Default:"Table of Contents"|String:"The title used for the ToC"|Tab3Parent:Table of Contents|Link:"https://quarto.org/docs/reference/formats/pdf.html#table-of-contents"|Linktext:?
	lof:checkbox|Type:boolean|Default:1|String:"Print a list of figures in the document"|Tab3Parent:Table of Contents|Link:"https://quarto.org/docs/reference/formats/pdf.html#table-of-contents"|Linktext:?
	lot:checkbox|Type:boolean|Default:1|String:"Print a list of tables in the document"|Tab3Parent:Table of Contents|Link:"https://quarto.org/docs/reference/formats/pdf.html#table-of-contents"|Linktext:?
	; ; Numbering
	number-depth:edit|Type:Integer|Default:3|String:"What is the maximum depth of sections that should be numbered?"|Max:99|Min:1|ctrlOptions:Number|Tab3Parent:Numbering|Link:"https://quarto.org/docs/reference/formats/pdf.html#numbering"|Linktext:?
	number-sections:checkbox|Type:boolean|Default:1|String:"Do you want to number your sections automatically?"|Tab3Parent:Numbering|Link:"https://quarto.org/docs/reference/formats/pdf.html#numbering"|Linktext:?
	; ;number-offset:edit|Type:Integer|Default:3|String:"What is the maximum depth of sections that should be numbered?"|Max:99|Min:1|ctrlOptions:Number|Tab3Parent:Numbering|Link:"https://quarto.org/docs/reference/formats/pdf.html#numbering"|Linktext:?
	shift-heading-level-by:edit|Type:Integer|Default:1|String:"Shift heading levels by a positive or negative integer (e.g. -1 or +2)"|ctrlOptions:Number|Tab3Parent:Numbering|Link:"https://quarto.org/docs/reference/formats/pdf.html#numbering"|Linktext:?
	; ;top-level-devision:checkbox|Type:boolean|Default:1|String:"Treat top-level headings as the given division type (default, section, chapter, or part)."|Tab3Parent:Numbering|Link:"https://quarto.org/docs/reference/formats/pdf.html#numbering"|Linktext:?
	; ; Fonts
	; mainfont
	; monofont
	; fontsize
	; fontenc
	; fontfamily
	; fontfamilyoptions
	; sansfont
	; mathfont
	; CJKmainfont
	; mainfontoptions
	; sansfontoptions
	; monofontoptions
	; mathfontoptions
	; CJKoptions
	; microtypeoptions
	; linestretch
	; Colors
	; linkcolor
	; filecolor
	; citecolor
	; urlcolor
	; toccolor
	; colorlinks
	; Layout
	; fig-cap-location
	; tbl-cap-location
	; documentclass
	; classoption
	; pagestyle
	; papersize
	; grid
	; margin-left
	; margin-right
	; margin-top
	; margin-bottom
	; geometry
	; hyperrefoptions
	; indent
	; block-headings
	; Code
	; code-line-numbers
	; code-annotaions
	; code-block-border-left
	; code-block-bg
	; highlight-style
	; syntax-definitions
	; listings
	; indented-code-classes
	; Execution
	; eval
	; echo
	; output
	; warning
	; error
	; include
	; cache
	; freeze
	; Figures
	fig-align:ddl|Type:String|Default:"default"|String:"Figure horizontal alignment"|ctrlOptions:default,left,right,center|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	; fig-env|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	fig-pos:edit|Type:String|Default:"H"|String:"LaTeX figure position arrangement to be used in \begin{figure}[]"|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	fig-cap-location:ddl|Type:String|Default:bottom|String:"Where to place figure captions"|ctrlOptions:top,bottom,margin|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	fig-height:edit|Type:Integer|Default:8|String:"Set default height in inches for figures"|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	fig-width:edit|Type:Integer|Default:8|String:"Set default width in inches for figures"|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	fig-format:ddl|Type:String|Default:png|String:"Default format for figures generated by Matplotlib or R graphics"|ctrlOptions:retina,png,jpeg,svg,pdf|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	fig-dpi:edit|Type:Integer|Default:96|String:"Default DPI for figures generated by Matplotlib or R graphics"|ctrlOptions:Number|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	; fig-asp|Tab3Parent:Figures|Link:"https://quarto.org/docs/reference/formats/pdf.html#figures"|Linktext:?
	; Tables
	tbl-colwidths:combobox|Type:String|Default:auto|String:"How to scale table column widths which ware wider than 'columns' characters (72 by default)?|Default:auto|ctrlOptions:auto,true,false|Tab3Parent:Tables|Link:"https://quarto.org/docs/reference/formats/pdf.html#tables"|Linktext:?
	tbl-cap-location:ddl|Type:String|Default:bottom|String:"Where to place table captions"|ctrlOptions:top,bottom,margin|Tab3Parent:Tables|Link:"https://quarto.org/docs/reference/formats/pdf.html#tables"|Linktext:?
	df-print:ddl|Type:String|Default:default|String:"Method used to print tables in Knitr engine documents"|ctrlOptions:default,kable,tibble,paged|Tab3Parent:Tables|Link:"https://quarto.org/docs/reference/formats/pdf.html#tables"|Linktext:?
	; References
	; bibliography|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; csl|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; cite-method|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; citeproc:checkbox|Type:boolean|Default:1|String:"Turn on built-in citation processing."|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; biblatexoptions:edit|Type:String|String:"A list of options for BibLaTeX"|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; natbiboptions:edit|Type:String|String:"One or more options to provide for natbib when generating a bibliography"|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; biblio-style:edit|Type:String|String:"The bibliography style to use (e.g. \bibliographystyle{dinat} when using natbib or biblatex"|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; biblio-title|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; biblio-config|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; citation-abbreviations|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; link-citations|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; link-bibliography|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; notes-after-punctuation|Tab3Parent:References|Link:"https://quarto.org/docs/reference/formats/pdf.html#references"|Linktext:?
	; Footnotes
	; links-as-notes|Tab3Parent:Footnotes|Link:"https://quarto.org/docs/reference/formats/pdf.html#footnotes"|Linktext:?
	; reference-location|Tab3Parent:Footnotes|Link:"https://quarto.org/docs/reference/formats/pdf.html#footnotes"|Linktext:?
	; Citation
	; citation|Tab3Parent:Citation|Link:"https://quarto.org/docs/reference/formats/pdf.html#citation"|Linktext:?
	; Language
	; lang|Tab3Parent:Language|Link:"https://quarto.org/docs/reference/formats/pdf.html#language"|Linktext:?
	; language|Tab3Parent:Language|Link:"https://quarto.org/docs/reference/formats/pdf.html#language"|Linktext:?
	; dir|Tab3Parent:Language|Link:"https://quarto.org/docs/reference/formats/pdf.html#language"|Linktext:?
	; Includes
	; include-before-body|Tab3Parent:Includes|Link:"https://quarto.org/docs/reference/formats/pdf.html#includes"|Linktext:?
	; include-after-body|Tab3Parent:Includes|Link:"https://quarto.org/docs/reference/formats/pdf.html#includes"|Linktext:?
	; include-in-header|Tab3Parent:Includes|Link:"https://quarto.org/docs/reference/formats/pdf.html#includes"|Linktext:?
	; metadata-files|Tab3Parent:Includes|Link:"https://quarto.org/docs/reference/formats/pdf.html#includes"|Linktext:?
	; Metadata
	; keywords|Tab3Parent:Metadata|Link:"https://quarto.org/docs/reference/formats/pdf.html#metadata"|Linktext:?
	; subject|Tab3Parent:Metadata|Link:"https://quarto.org/docs/reference/formats/pdf.html#metadata"|Linktext:?
	; title-meta|Tab3Parent:Metadata|Link:"https://quarto.org/docs/reference/formats/pdf.html#metadata"|Linktext:?
	; author-meta|Tab3Parent:Metadata|Link:"https://quarto.org/docs/reference/formats/pdf.html#metadata"|Linktext:?
	; date-meta|Tab3Parent:Metadata|Link:"https://quarto.org/docs/reference/formats/pdf.html#metadata"|Linktext:?
	; Rendering
	; from|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; output-file|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; output-ext|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; template|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; template-partials|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; standalone|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; filters|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; shortcodes|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; keep-md|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; keep-ipynb|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; ipynb-filters|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; keep-tex|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; extract-media|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; resource-path|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; default-image-extension|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; abbreviations|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; dpi|Tab3Parent:Rendering|Link:"https://quarto.org/docs/reference/formats/pdf.html#rendering"|Linktext:?
	; ; Latexmk
	latex-auto-mk:checkbox|Type:boolean|Default:1|String:"Use Quarto's built-in PDF rendering wrapper (includes support for automatically installing missing LaTeX packages)"|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	latex-auto-install:checkbox|Type:boolean|Default:1|String:"Enable/disable automatic LaTeX package installation"|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	latex-min-runs:edit|Type:number|Default:1|String:"Minimum number of compilation passes."|ctrlOptions:number|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	latex-max-runs:edit|Type:number|Default:5|String:"Minimum number of compilation passes."|ctrlOptions:number|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	;latex-clean|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	;latex-makeindex|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	;latex-makeindex-opts|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	;latex-tlmgr-opts|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	;latex-output-dir|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	;latex-tinytex:checkbox|Type:boolean|Default:0|String:"Use tinytex for pdf-compilation?"|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	;latex-input-paths|Tab3Parent:Latexmk|Link:"https://quarto.org/docs/reference/formats/pdf.html#latexmk"|Linktext:?
	; Text Output
	; ascii
	; Meta
	renderingpackage_start:Meta|Value:quarto::quarto_render("index.qmd",execute_params = list(
	renderingpackage_end:Meta|Value:),output_format = "pdf","%name%.pdf")
	filesuffix:Meta|Value:pdf
	inputsuffix:Meta|Value:qmd
	dateformat:Meta|Value:{A_DD}.{A_MM}.{A_YYYY}
	package:Meta|Value:quarto
	;|Link:"https://quarto.org/docs/reference/formats/pdf.html#format-options"|Tab3Parent:Format options|Linktext:?
	;Link:"https://quarto.org/docs/reference/formats/pdf.html#format-options"|Linktext:?

"""

    ### Getters

    def get_config(self, type="settings"):
        if type in ["settings"]:
            return self.applied_settings
        elif type in ["pipeline"]:
            return self.applied_pipeline
        elif type in ["format_definitions"]:
            return self.applied_format_definitons
        elif type in ["file_history"]:
            return self.file_history

    ### Loaders

    def load_default_settings(self):
        """Load default settings values."""
        # Initialize with values directly in the class
        return self.default_settings.copy()

    def load_default_pipeline(self):
        """Load default pipeline-yaml."""
        # Initialize with values directly in the class
        return yaml.safe_load(self.default_pipeline_yaml)

    def load_default_format_definitions(self):
        """Load default pipeline-yaml."""
        # Initialize with values directly in the class
        return self.default_format_definitions

    ### Misc

    def validate(self):
        """Validate the current configuration and raise errors if invalid."""
        # Add validation rules, e.g., checking required fields or valid ranges
        if 'setting1' not in self.config:
            raise ValueError("Configuration missing 'setting1'")
        # Add additional validation as needed
        print("Configuration validated successfully.")

    def merge(self, custom_config_path):
        """
        Merge options from a custom YAML config file into the runtime configuration.
        This only applies to the configuration itself, NOT to pipeline or format_definitions

        If those are to be modified, expoert them first, modify them and pass them in as file-paths,
        by which they will **fully replace** the defaults.

        """
        try:
            with open(custom_config_path, 'r', encoding='utf-8') as f:
                custom_config = yaml.safe_load(f)

            # Update main config with custom settings, ignoring extra fields
            self.config.update(custom_config)
            print(f"Configuration merged with {custom_config_path}")
        except FileNotFoundError:
            print(
                f"Custom configuration file not found at {custom_config_path}. No merge performed."
            )
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")

    def load_cli_args(self):
        """Load and apply command-line arguments, if any."""
        pass
        parser = argparse.ArgumentParser(description="Process configuration options.")
        parser.add_argument(
            '--pipeline', type=str, help="Path to the pipeline YAML file"
        )
        parser.add_argument(
            '--format_def', type=str, help="Path to the format definitions file"
        )
        args = parser.parse_args()

        # Update paths if provided via CLI
        if args.pipeline:
            self.config['pipeline_path'] = args.pipeline
        if args.format_def:
            self.config['format_def_path'] = args.format_def

    def load_last_run(self, last_run_path=None):
        """Load last run configuration for GUI mode, merging with defaults."""
        if last_run_path is not None:
            try:
                with open(last_run_path, 'r', encoding='utf-8') as f:
                    last_run_config = yaml.safe_load(f)
                self.applied_settings.update(last_run_config)
                print("Last run configuration loaded for GUI mode.")
            except FileNotFoundError:
                print("Last run configuration not found; using default configuration.")

    def save_last_run(self, last_run_path=None):
        """Save the current configuration as the last run configuration."""
        if last_run_path is not None:
            try:
                with open(last_run_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self.applied_settings, f, allow_unicode=True)
                print(f"Configuration saved to {last_run_path}")
            except FileNotFoundError:
                print("Last run configuration not found; changes not saved.")

    def load_file_history(self, file_history_path=None):
        """Load the file-history"""
        if file_history_path is not None:
            try:
                with open(file_history_path, 'r', encoding='utf-8') as f:
                    file_history_config = yaml.safe_load(f)
                self.file_history.extend(file_history_config)
                print("File-history-config loaded for GUI mode.")
            except FileNotFoundError:
                print("File-history-configuration not found; using no configuration.")

    ### EXPORTERS ###
    def export_config(self, default=False, file_path=None):
        """Export the current configuration (modified or default) to a YAML file."""
        if file_path is not None:
            with open(file_path, 'w', encoding='utf-8') as f:
                if default:
                    yaml.dump(self.default_settings, f, allow_unicode=True)
                else:
                    yaml.dump(self.applied_settings, f, allow_unicode=True)
            print(f"Custom configuration exported to {file_path}")
        else:
            print(self.applied_settings)

    def get_pipeline_path(self):
        """Return the path to the pipeline configuration."""
        return self.config.get('pipeline_path', 'default_pipeline.yml')

    def get_format_def_path(self):
        """Return the path to the format definitions file."""
        return self.config.get('format_def_path', 'default_format_definitions.txt')


# # initialise
# CH = ConfigurationHandler()
# CH.apply_defaults()

# # retrieve current configurations into objects
# format_definitions_string = CH.get_config("format_definitions")
# settings = CH.get_config("settings")
# pipeline = CH.get_config("pipeline")

# # export default/custom configurations
# CH.export_config(default=True)  # to commandline
# CH.export_config(default=False, file_path="dev/configuration.yml")  # to file

# ##TODO##
# #
# CH.load_last_run(last_run_path=None)
# CH.save_last_run(last_run_path=None)
# print("DD")
