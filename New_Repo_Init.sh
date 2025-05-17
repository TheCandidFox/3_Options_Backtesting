#!/bin/bash

# Prompt for new GitHub repo URL
read -p "Enter new GitHub repo URL (e.g., https://github.com/user/myrepo.git): " RAW_URL

# Trim whitespace and validate
NEW_REPO_URL=$(echo "$RAW_URL" | tr -d '\n' | xargs)
if [[ -z "$NEW_REPO_URL" ]]; then
  echo "❌ Error: No URL entered. Exiting."
  exit 1
fi

# Extract repo nameKs
REPO_NAME=$(basename -s .git "$NEW_REPO_URL")
if [[ -z "$REPO_NAME" ]]; then
  echo "❌ Error: Invalid URL format. Make sure it ends in .git"
  exit 1
fi

# Resolve destination folder path (sibling to current folder)
SOURCE_DIR="$PWD"
TARGET_DIR="$(dirname "$PWD")/$REPO_NAME"

echo ""
echo "🌱 Preparing to scaffold new repo:"
echo "→ Source folder: $SOURCE_DIR"
echo "→ Target folder: $TARGET_DIR"
echo "→ New Git remote: $NEW_REPO_URL"
echo ""

# Check if target folder already exists
if [[ -d "$TARGET_DIR" ]]; then
  # List all items in the folder except .git
  NON_GIT_CONTENT=$(find "$TARGET_DIR" -mindepth 1 -not -name '.git' -not -path "$TARGET_DIR/.git*" | wc -l)

  if [[ "$NON_GIT_CONTENT" -gt 0 ]]; then
    echo "❌ Error: Target folder '$REPO_NAME' contains user content. Aborting to prevent overwrite."
    exit 1
  else
    echo "⚠️ Target folder '$REPO_NAME' only contains .git/ (empty repo clone). Proceeding."
  fi
else
  mkdir "$TARGET_DIR"
  echo "✅ Created folder: $REPO_NAME"
fi


# Copy contents from template repo to new folder (excluding .git)
shopt -s dotglob  # to include hidden files like .env
for item in "$SOURCE_DIR"/*; do
  if [[ "$(basename "$item")" != ".git" ]]; then
    cp -r "$item" "$TARGET_DIR/"
  fi
done
shopt -u dotglob

# Change into target directory
cd "$TARGET_DIR" || {
  echo "❌ Failed to enter target directory."
  exit 1
}

# Initialize Git if not already initialized
if [[ ! -d .git ]]; then
  git init
fi

# Add remote and commit
git remote remove origin 2>/dev/null
git remote add origin "$NEW_REPO_URL"

git add .
git commit -m "New Setup from Template"

# Create and push to 'main' branch
git branch -M main
git push -u origin main

echo ""
echo "✅ Successfully set up new repo '$REPO_NAME' and pushed contents."
