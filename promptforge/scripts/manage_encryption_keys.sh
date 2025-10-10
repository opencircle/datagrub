#!/bin/bash
#
# Encryption Key Management Script
#
# Manage encryption keys for different environments (development, staging, production)
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  list                  - List all encryption keys"
    echo "  add <env> <key>       - Add encryption key for environment"
    echo "  generate <env>        - Generate and add new key for environment"
    echo "  rotate <env>          - Rotate key for environment (generates new key)"
    echo "  test <env>            - Test encryption with key from environment"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 generate staging"
    echo "  $0 generate production"
    echo "  $0 test staging"
    echo ""
}

list_keys() {
    echo -e "${YELLOW}Encryption Keys:${NC}"
    echo ""
    docker exec promptforge-postgres psql -U promptforge -d promptforge -c "
        SELECT
            environment,
            substring(key_value, 1, 20) || '...' as key_preview,
            is_active,
            created_at::date as created
        FROM encryption_keys
        ORDER BY environment;
    "
}

generate_key() {
    docker exec promptforge-api python -c "
from app.services.encryption import EncryptionService
print(EncryptionService.generate_encryption_key())
"
}

add_key() {
    local env=$1
    local key=$2

    if [ -z "$env" ] || [ -z "$key" ]; then
        echo -e "${RED}Error: Environment and key are required${NC}"
        show_usage
        exit 1
    fi

    echo -e "${YELLOW}Adding encryption key for environment: $env${NC}"

    # Check if key already exists
    EXISTS=$(docker exec promptforge-postgres psql -U promptforge -d promptforge -t -c "
        SELECT COUNT(*) FROM encryption_keys WHERE environment = '$env' AND is_active = true;
    " | tr -d ' ')

    if [ "$EXISTS" != "0" ]; then
        echo -e "${RED}Error: Active key already exists for environment: $env${NC}"
        echo "Use 'rotate' command to replace it"
        exit 1
    fi

    # Insert key
    docker exec promptforge-postgres psql -U promptforge -d promptforge -c "
        INSERT INTO encryption_keys (id, environment, key_value, description, is_active)
        VALUES (
            gen_random_uuid(),
            '$env',
            '$key',
            'Encryption key for $env environment',
            true
        );
    "

    echo -e "${GREEN}✓ Key added successfully${NC}"
    list_keys
}

generate_and_add() {
    local env=$1

    if [ -z "$env" ]; then
        echo -e "${RED}Error: Environment is required${NC}"
        show_usage
        exit 1
    fi

    echo -e "${YELLOW}Generating new encryption key for: $env${NC}"

    # Generate key
    NEW_KEY=$(generate_key)

    echo -e "${GREEN}Generated key: $NEW_KEY${NC}"
    echo ""

    # Add to database
    add_key "$env" "$NEW_KEY"
}

rotate_key() {
    local env=$1

    if [ -z "$env" ]; then
        echo -e "${RED}Error: Environment is required${NC}"
        show_usage
        exit 1
    fi

    echo -e "${YELLOW}Rotating encryption key for: $env${NC}"
    echo -e "${RED}WARNING: This will deactivate the old key and generate a new one${NC}"
    echo -e "${RED}WARNING: Existing encrypted data will NOT be re-encrypted automatically${NC}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "Aborted"
        exit 0
    fi

    # Deactivate old key
    docker exec promptforge-postgres psql -U promptforge -d promptforge -c "
        UPDATE encryption_keys
        SET is_active = false, rotated_at = NOW()::text
        WHERE environment = '$env' AND is_active = true;
    "

    # Generate and add new key
    generate_and_add "$env"

    echo ""
    echo -e "${YELLOW}IMPORTANT: You need to re-encrypt existing data with the new key${NC}"
    echo "Run: docker exec promptforge-api python scripts/re_encrypt_provider_keys.py --env $env"
}

test_encryption() {
    local env=$1

    if [ -z "$env" ]; then
        env="development"
    fi

    echo -e "${YELLOW}Testing encryption for environment: $env${NC}"

    # Set environment variable and test
    docker exec -e PROMPTFORGE_ENV=$env promptforge-api python -c "
import os
os.environ['PROMPTFORGE_ENV'] = '$env'

from app.services.encryption import EncryptionService

print('Initializing encryption service...')
e = EncryptionService()

# Test encrypt/decrypt
test_key = 'sk-test-key-123456789'
print(f'Encrypting: {test_key}')

encrypted, hash_val = e.encrypt_api_key(test_key)
print(f'Encrypted: {encrypted[:30]}...')

decrypted = e.decrypt_api_key(encrypted)
print(f'Decrypted: {decrypted}')

if decrypted == test_key:
    print('✓ Encryption test PASSED')
else:
    print('✗ Encryption test FAILED')
    exit(1)
"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Encryption test successful for environment: $env${NC}"
    else
        echo -e "${RED}✗ Encryption test failed${NC}"
        exit 1
    fi
}

# Main
case "$1" in
    list)
        list_keys
        ;;
    add)
        add_key "$2" "$3"
        ;;
    generate)
        generate_and_add "$2"
        ;;
    rotate)
        rotate_key "$2"
        ;;
    test)
        test_encryption "$2"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
