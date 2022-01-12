import fitz
import json
from argparse import ArgumentParser

# https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_text


def get_pdf_list_from_sf_log(siegfried_log_path):
    pdf_list = []
    with open(siegfried_log_path, "r") as sf_log:
        for line in sf_log:
            sf_file_json = json.loads(line)
            for f in sf_file_json["files"]:
                if "Acrobat PDF" in f["matches"][0]["format"]:
                    pdf_list.append(f["filename"])
    return pdf_list


def identify_image(pdf_file):
    doc = fitz.open(pdf_file)
    for page in doc:
        if page.get_text():
            return {"isText": True}
        else:
            return {"isText": False}
    doc.close()


def create_pdf_info(pdf):
    if identify_image(pdf):
        pdf_info = {pdf: identify_image(pdf)}
        pdf_info[pdf].update({"tool_version_info": fitz.__doc__})
        return pdf_info


def write_pdf_analyser_log(pdf_infos, output_file):
    output = open(output_file, "w", encoding="utf-8") #Todo: add timestamp to the filename and or the sf_log_name
    json.dump(pdf_infos, output, sort_keys=True, ensure_ascii=True)
    output.write("\n")


def main(siegfried_log_path, output_file):
    counter = 0
    pdf_list = get_pdf_list_from_sf_log(siegfried_log_path)
    pdf_infos = {}
    for pdf in pdf_list:
        pdf_info = create_pdf_info(pdf)
        if pdf_info:
            pdf_infos.update(pdf_info)
            counter += 1
            print("{} files of the siegfried log file {} processed.".format(
                counter, siegfried_log_path))
        else:
            print("The file {} has not returned any information, make sure that its not corrupted and opened properly with fitz.".format(pdf))

    write_pdf_analyser_log(pdf_infos, output_file)


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
