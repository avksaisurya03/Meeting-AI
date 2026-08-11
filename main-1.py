import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


from core.preprocessor import preprocess_transcript
from core.analyzer import analyze_meeting
from core.exporters import export_json, export_markdown, save_outputs


def get_meeting_file():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not Path(filename).exists():
            raise FileNotFoundError(f"{filename} was not found.")
        return filename

    meeting_files = sorted(Path(".").glob("Meeting-*.txt")) + sorted(Path("Data").glob("Meeting-*.txt"))
    if not meeting_files:
        raise FileNotFoundError("No Meeting-*.txt files were found.")

    print("\nAvailable meeting files:\n")
    for index, file in enumerate(meeting_files, start=1):
        print(f"{index}. {file}")

    while True:
        choice = input("\nEnter meeting number: ")
        try:
            number = int(choice)
            if 1 <= number <= len(meeting_files):
                return str(meeting_files[number - 1])
            print(f"Please enter a number from 1 to {len(meeting_files)}.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    print("=" * 60)
    print("MEETING MIND AI - ENGINE")
    print("=" * 60)

    meeting_file = get_meeting_file()
    print(f"\nSelected: {meeting_file}")

    raw_text = Path(meeting_file).read_text(encoding="utf-8")
    cleaned_text = preprocess_transcript(raw_text)

    print("\nSending transcript to Azure OpenAI...")
    result = analyze_meeting(cleaned_text)

    # Print summary & Markdown table
    md_report = export_markdown(result)
    print("\n" + "=" * 60)
    print(md_report)
    print("=" * 60)

    json_file, md_file = save_outputs(result, meeting_file)
    print(f"\nJSON File created: {json_file.absolute()}")
    print(f"Markdown Report created: {md_file.absolute()}")


if __name__ == "__main__":
    main()