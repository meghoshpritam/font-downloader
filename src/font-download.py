import re

import requests


def read_file(file_path):
    r_file = open(file_path, "r")
    return r_file.read()


def write_file(file_path, content):
    r_file = open(file_path, "w")
    return r_file.write(content)


def get_css_font_configs(file_content):
    configs = []
    config_texts = list(filter(lambda x: len(x) > 10, file_content.split("/*")))
    for config_text in config_texts:
        lines = config_text.split("\n")
        configs.append(
            {
                "comment": lines[0].replace("*/", "").strip(),
                "fontFamily": re.sub(
                    r"[;'\"]", "", lines[2].replace("font-family:", "")
                ).strip(),
                "fontStyle": re.sub(
                    r"[;'\"]", "", lines[3].replace("font-style:", "")
                ).strip(),
                "fontWeight": re.sub(
                    r"[;'\"]", "", lines[4].replace("font-weight:", "")
                ).strip(),
                "fontStretch": re.sub(
                    r"[;'\"]", "", lines[5].replace("font-stretch:", "")
                ).strip(),
                "fontDisplay": re.sub(
                    r"[;'\"]", "", lines[6].replace("font-display:", "")
                ).strip(),
                "src": lines[7].split("(")[1].split(")")[0],
                "format": re.sub(
                    r"[;'\"]", "", lines[7].split("format(")[1].split(")")[0]
                ),
                "unicodeRange": re.sub(
                    r"[;'\"]", "", lines[8].replace("unicode-range:", "")
                ).strip(),
            }
        )

    return configs


def download_fonts(configs):
    num_configs = len(configs)
    idx = 0
    downloaded_urls = []
    for config in configs:
        idx += 1
        src = config["src"]
        if src in downloaded_urls:
            print(f"Skip {idx}/{num_configs} --> {src}")
            continue
        downloaded_urls.append(src)
        file_name = config["file"]
        print(f"Downloading {idx}/{num_configs} --> {file_name}")
        response = requests.get(src)
        open(f"./fonts/{file_name}", "wb").write(response.content)


def update_file_names_to_config(configs):
    new_configs = []
    for config in configs:
        local_config = config
        font_family = re.sub(r"\s", "", config["fontFamily"])
        file_name = f"{font_family}-{config['comment']}-{config['fontStyle']}.{config['format']}"
        local_config["file"] = file_name
        new_configs.append(local_config)

    return new_configs


def generate_css_font_config(
    configs, static_prefix, use_font_weight=True, use_font_stretch=False
):
    content = ""
    for config in configs:
        content += f"/* {config['fontFamily']} {config['comment']} */\n"
        content += "@font-face {\n"
        content += f"  font-family: \"{config['fontFamily']}\";\n"
        content += f"  font-style: {config['fontStyle']};\n"
        if use_font_weight:
            content += f"  font-weight: {config['fontWeight']};\n"
        if use_font_stretch:
            content += f"  font-stretch: {config['fontStretch']};\n"
        content += f"  font-display: {config['fontDisplay']};\n"
        content += f"  src: url('{static_prefix}{config['file']}') format('{config['format']}');\n"
        content += f"  unicode-range: {config['unicodeRange']};\n"
        content += "}\n\n"

    return content


def generate_css_font_compact_config(configs, static_prefix):
    minified_config = []
    urls = []
    for config in configs:
        src = config["src"]
        if src in urls:
            continue
        urls.append(src)
        minified_config.append(config)

    return generate_css_font_config(
        minified_config, static_prefix, use_font_weight=False
    )


def main():
    input_file_name = "../open-sans-font.css"
    output_file_name = "../dist/fonts.css"
    css_font_path_prefix = ""

    file_content = read_file(input_file_name)
    configs = get_css_font_configs(file_content)
    configs = update_file_names_to_config(configs)
    download_fonts(configs)
    content_to_save = generate_css_font_config(configs, css_font_path_prefix)
    content_to_save_compact = generate_css_font_compact_config(
        configs, css_font_path_prefix
    )
    write_file(output_file_name, content_to_save)
    write_file(
        output_file_name.replace(".css", "-compact.css"), content_to_save_compact
    )


if __name__ == "__main__":
    main()
