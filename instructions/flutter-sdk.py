from scrape.runner.powershell import run_powershell_with_text_output
from scrape.extract.matcher import extract_words_by_pattern,VERSION_PATTERN
from scrape.instruction import Response,compare_app_version


def main(requirements: dict[str, str]):
    command = r"flutter --version"
    output = run_powershell_with_text_output(command)
    
    if output['stderr']:
        return Response(False, output['stderr'])
    
    result = extract_words_by_pattern(output["stdout"], VERSION_PATTERN)
    
    if not result:
        return Response(False, "Failed to extract version")
    
    if compare_app_version(result[0], requirements, "Flutter")["status"]:
        print("Flutter version is correct")
    else:
        print("Flutter version is incorrect")

    
    
if __name__ == "__main__":
    main({"target": None, "minimum": "1.0.0"})