#!/bin/bash
# package.sh — builds app.zip for uploading to AWS Lambda
# Usage: bash package.sh

set -e

echo "Installing dependencies into ./package/ ..."
pip3 install -r requirements.txt --target ./package --quiet

echo "Copying app files ..."
cp -r app.py lambda_handler.py db.py routes templates static ./package/

echo "Stamping build_info.json ..."
cat > ./package/build_info.json << EOF
{
  "version": "1.0.0",
  "deploy_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "commit_sha": "$(git rev-parse HEAD)"
}
EOF

echo "Creating app.zip ..."
cd package
zip -r ../app.zip . --quiet
cd ..
rm -rf package

echo "Done — app.zip is ready to upload to Lambda."
ls -lh app.zip
