#!/bin/bash

# Script to create remaining MFEs based on template

MFES=("evaluations:3002:LineChart" "playground:3003:PlayCircle" "traces:3004:Activity" "policy:3005:Shield" "models:3006:Brain")

for MFE_INFO in "${MFES[@]}"; do
    IFS=':' read -r MFE_NAME PORT ICON <<< "$MFE_INFO"
    MFE_DIR="mfe-${MFE_NAME}"

    echo "Creating ${MFE_NAME} MFE..."

    # Create directory structure
    mkdir -p "${MFE_DIR}"/{src,public}

    # Copy configuration files
    cp mfe-projects/tsconfig.json "${MFE_DIR}/"
    cp mfe-projects/tailwind.config.js "${MFE_DIR}/"
    cp mfe-projects/postcss.config.js "${MFE_DIR}/"
    cp mfe-projects/.babelrc "${MFE_DIR}/"

    echo "✓ Created ${MFE_NAME} structure"
done

echo "All MFEs created successfully!"
