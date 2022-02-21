import fitz
import json
import re
from argparse import ArgumentParser


# https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_text


# Todo: If pdf list is empty print out warning that there is no entry with Acrobat PDF in sf log
def get_pdf_list_from_sf_log(siegfried_log_path):
    pdf_list = []
    with open(siegfried_log_path, "r") as sf_log:
        for line in sf_log:
            sf_file_json = json.loads(line)
            for f in sf_file_json["files"]:
                if "Acrobat PDF" in f["matches"][0]["format"]:
                    pdf_list.append(f["filename"])
    if not pdf_list:
        print(
            "It seems like there is no file with the format 'Acrobat PDF' in the siegfried log")
    return pdf_list


def get_font_list(pdf_file):
    try:
        doc = fitz.open(pdf_file)
        list_of_fonts = []
        list_of_unique_fonts = []
        cleaned_font_infos = []
        for page in doc:
            fonts_on_page = page.get_fonts()
            list_of_fonts.extend(fonts_on_page)
            list_of_unique_fonts = list(set(list_of_fonts) | set(fonts_on_page))
        for font in list_of_unique_fonts:
            cleaned_font_infos.append(clear_font_info(font))
        return cleaned_font_infos
    except RuntimeError:
        print("{} was not opened properly and can't be identified".format(
            pdf_file))
    except ValueError:
        print("{} seems to be an encrypted file and can't be identified".format(
            pdf_file))


def clear_font_info(font):
    font_info = {'font-name': delete_junk_chars(font[3])}
    font_info.update({'font-no': font[0]})
    font_info.update({'PostScript-type': font[2]})
    font_info.update({'is_embedded': is_embedded(font[3])})
    return font_info


def is_embedded(font_name):
    print(font_name)
    split_name = re.split(r'\+', font_name)
    if len(split_name) > 1:
        return True
    else:
        return False


def delete_junk_chars(font_name):
    # Todo: What if there is a plus in the font name?
    split_name = re.split(r'\+',font_name)
    if len(split_name) > 1:
        cleaned_font_name = split_name[1]
        return cleaned_font_name
    else:
        return split_name[0]


def get_word_count(pdf):
    list_of_words = []
    try:
        doc = fitz.open(pdf)
        for page in doc:
            words = page.get_text('words')
            list_of_words.extend(words)
        return len(list_of_words)
    except RuntimeError:
        print("{} was not opened properly and can't be identified".format(
            pdf))
    except ValueError:
        print("{} seems to be an encrypted file and can't be identified".format(
            pdf))


def is_image(pdf_file):
    try:
        doc = fitz.open(pdf_file)
        for page in doc:
            if page.get_text():
                return False
            else:
                return True
        doc.close()
    except RuntimeError:
        print("{} was not opened properly and can't be identified".format(
            pdf_file))
        return "Error"
    except ValueError:
        print("{} seems to be an encrypted file and can't be identified".format(
            pdf_file))
        return "Error"


def write_pdf_analyser_log(pdf_infos, output_file):
    output = open(output_file, "w",
                  encoding="utf-8")  # Todo: add timestamp to the filename and or the sf_log_name and json ending
    json.dump(pdf_infos, output, sort_keys=True, ensure_ascii=True)
    output.write("\n")


def main(siegfried_log_path, output_file):
    counter = 0
    pdf_list = get_pdf_list_from_sf_log(siegfried_log_path)
    pdf_infos = {}
    for pdf in pdf_list:
        counter +=1
        print(f"{counter} pdf files processed")
        if is_image(pdf) == "Error":
            continue
        elif is_image(pdf) is not True:
            pdf_infos[pdf] = {"isImage": False}
            pdf_infos[pdf].update({"word_count": get_word_count(pdf)})
            pdf_infos[pdf].update({"list_of_fonts": get_font_list(pdf)})
            pdf_infos[pdf].update({"tool_version_info": fitz.__doc__})
        else:
            pdf_infos[pdf] = {"isImage": True}
            pdf_infos[pdf].update({"tool_version_info": fitz.__doc__}) # TODO: I should fix that duplicate from l. 127, however, if I put that outside the if statement I get a key error.

    write_pdf_analyser_log(pdf_infos, output_file)


#Todo: Write Clean up method and find out what exactly junk chars indicate. How embedded fonts look


if __name__ == "__main__":
    parser = ArgumentParser(description="...")
    parser.add_argument("-siegfried_log_path", metavar="siegfried_log_path",
                        help="Path to the siegfried log file containing the "
                             "needed file format information")
    parser.add_argument("-dest_file_path", "--dest_file_path",
                        dest="dest_file_path",
                        help="Path to write the pdf_anaylser log")
    args = parser.parse_args()
    main(args.siegfried_log_path, args.dest_file_path)
