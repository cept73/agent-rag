import argparse, json, os, uvicorn
from .api import app
from . import db


def import_folder(folder, slot):
    db.init()
    imported, skipped = [], []
    for root, _, files in os.walk(folder):
        for filename in sorted(files):
            path = os.path.join(root, filename)
            try:
                with open(path, encoding="utf-8") as file:
                    content = file.read()
                if not content.strip():
                    skipped.append({"file": path, "reason": "пустой файл"})
                    continue
                name = os.path.relpath(path, folder)
                imported.append({"id": db.add(slot, name, content), "file": name})
            except (OSError, UnicodeDecodeError):
                skipped.append(
                    {"file": path, "reason": "не удалось прочитать UTF-8 файл"}
                )
    print(
        json.dumps(
            {"success": True, "slot": slot, "imported": imported, "skipped": skipped},
            ensure_ascii=False,
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", choices=["import"])
    parser.add_argument("--folder")
    parser.add_argument("--slot")
    args = parser.parse_args()
    if args.command == "import":
        if not args.folder or not args.slot or not os.path.isdir(args.folder):
            print(
                json.dumps(
                    {
                        "success": False,
                        "answer": "Укажите существующие --folder и --slot.",
                    },
                    ensure_ascii=False,
                )
            )
        else:
            import_folder(args.folder, args.slot)
    else:
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("RAG_PORT", "8000")))


if __name__ == "__main__":
    main()
