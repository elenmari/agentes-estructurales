#!/bin/bash

source venv/Scripts/activate

# Source the .env file to get the SSH key file path
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found."
    exit 1
fi

# Check if the SSH key file path is provided in the .env file
if [ -z "$SSH_PATH" ]; then
    echo "Error: SSH_PRIVATE_KEY_FILE not found in .env file."
    exit 1
fi

# Check if the SSH key file exists
if [ ! -f "$SSH_PATH" ]; then
    echo "Error: SSH private key file not found: $SSH_PATH"
    exit 1
fi

# Initialize ssh-agent
eval $(ssh-agent -s)

# Add the SSH key file to the agent with passphrase
ssh-add -k "$SSH_PATH"

echo "SSH agent initialized and key from file added successfully."