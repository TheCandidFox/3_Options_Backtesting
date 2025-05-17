#!/bin/bash

# Optional: Wipe existing venv (uncomment if you want a reset)
# rm -rf venv

# ✅ Safety check: Set core.autocrlf to true if not already configured
if ! git config --global core.autocrlf > /dev/null; then
    git config --global core.autocrlf true
    echo "Set core.autocrlf to true (first-time setup)"
fi

# Create venv
if command -v python3.12 &> /dev/null; then
    python3.12 -m venv venv
elif command -v py &> /dev/null; then
    py -3.12 -m venv venv
else
    echo "❌ Python 3.12 not found"
    exit 1
fi


# Detect OS and activate venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
elif [[ "$OSTYPE" == "darwin" || "$OSTYPE" == "linux-gnu" ]]; then
    source venv/bin/activate
else
    echo "❌ Venv not activated"
    exit 1
fi

# Upgrade pip
python -m pip install --upgrade pip==25.1.1

# Install dependencies
pip install -r requirements.txt

# Detect OS and set the correct interpreter path
mkdir -p .vscode

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    pythonPath="venv/Scripts/python.exe"
else
    pythonPath="venv/bin/python"
fi

cat << EOF > .vscode/settings.json
{
  "python.defaultInterpreterPath": "$pythonPath"
}
EOF

# ✅ Final user instructions
echo ""
echo "✅ Setup complete."
echo "Activate your virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    echo "   source venv/Scripts/activate"
else
    echo "   source venv/bin/activate"
fi
echo ""
