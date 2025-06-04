import os
import zipfile
import pathspec
import argparse
import datetime

def load_gitignore(gitignore_path):
    if not os.path.exists(gitignore_path):
        print(f"No .gitignore found at {gitignore_path}, proceeding without exclusions.")
        return pathspec.PathSpec.from_lines('gitwildmatch', [])
    with open(gitignore_path) as f:
        lines = f.readlines()
    spec = pathspec.PathSpec.from_lines('gitwildmatch', lines)
    print(f"Loaded .gitignore with {len(lines)} patterns.")
    return spec

def zip_project(source_dir, output_filename, gitignore_path=".gitignore"):
    spec = load_gitignore(os.path.join(source_dir, gitignore_path))

    total_files = 0
    added_files = 0

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            rel_root = os.path.relpath(root, source_dir)
            if rel_root == '.':
                rel_root = ''
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(rel_root, d))]

            for file in files:
                total_files += 1
                rel_file = os.path.join(rel_root, file)
                full_path = os.path.join(root, file)
                if not spec.match_file(rel_file):
                    zipf.write(full_path, rel_file)
                    added_files += 1
                    print(f"Adding:   {rel_file}")
                else:
                    print(f"Skipping: {rel_file}")

    print(f"\n✅ Done! {added_files} files added to {output_filename}. {total_files - added_files} files excluded.")

def get_default_output_filename():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"project_backup_{timestamp}.zip"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zip project while respecting .gitignore")
    parser.add_argument("--dir", default=".", help="Project directory to zip (default: current directory)")
    parser.add_argument("--output", help="Output zip file name (default: timestamped filename)")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.dir)
    output_file = args.output or get_default_output_filename()

    print(f"📦 Zipping project: {project_dir}")
    print(f"📄 Output file: {output_file}\n")

    zip_project(project_dir, output_file)
