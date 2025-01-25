#!/bin/bash

API_URL="http://localhost:8000"

# Test health endpoint
echo "Testing health endpoint..."
curl -s "${API_URL}/health"
echo -e "\n"

# Test generate_storyboard
echo "Testing generate_storyboard endpoint..."
STORYBOARD=$(curl -s -X POST "${API_URL}/generate_storyboard")
echo "$STORYBOARD"
echo -e "\n"

# Save storyboard for subsequent requests
echo "$STORYBOARD" > /tmp/storyboard.json

# Test generate_interruption
echo "Testing generate_interruption - Scenario 1 (Medium difficulty)..."
curl -s -X POST "${API_URL}/generate_interruption" \
  -H "Content-Type: application/json" \
  -d '{
    "storyboard": '"$(cat /tmp/storyboard.json)"',
    "current_text": "Your Honor, my client is clearly innocent because...",
    "question": "What was your client doing at the time of the crime?",
    "difficulty": 5,
    "past_interruptions": []
  }'
echo -e "\n"

echo "Testing generate_interruption - Scenario 2 (Low difficulty)..."
curl -s -X POST "${API_URL}/generate_interruption" \
  -H "Content-Type: application/json" \
  -d '{
    "storyboard": '"$(cat /tmp/storyboard.json)"',
    "current_text": "Your Honor, my client is clearly innocent because",
    "question": "What was your client doing at the time of the crime?",
    "difficulty": 3,
    "past_interruptions": ["BANANA!", "I love pickles"]
  }'
echo -e "\n"

echo "Testing generate_interruption - Scenario 3 (Low difficulty, different context)..."
curl -s -X POST "${API_URL}/generate_interruption" \
  -H "Content-Type: application/json" \
  -d '{
    "storyboard": '"$(cat /tmp/storyboard.json)"',
    "current_text": "Your Honor, it does not",
    "question": "Is it real that your client is bad at math?",
    "difficulty": 3,
    "past_interruptions": ["My client is guilty!"]
  }'
echo -e "\n"

echo "Testing generate_interruption - Scenario 4 (High difficulty)..."
curl -s -X POST "${API_URL}/generate_interruption" \
  -H "Content-Type: application/json" \
  -d '{
    "storyboard": '"$(cat /tmp/storyboard.json)"',
    "current_text": "I can assure you that my client would never",
    "question": "How do you explain the evidence found at the scene?",
    "difficulty": 8,
    "past_interruptions": ["BANANA!", "I love pickles", "My client is guilty!", "The prosecution is right"]
  }'
echo -e "\n"

echo "Testing generate_interruption - Scenario 5 (Maximum difficulty)..."
curl -s -X POST "${API_URL}/generate_interruption" \
  -H "Content-Type: application/json" \
  -d '{
    "storyboard": '"$(cat /tmp/storyboard.json)"',
    "current_text": "The prosecutions argument is fundamentally flawed because",
    "question": "Can you explain your clients alibi?",
    "difficulty": 10,
    "past_interruptions": ["BANANA!", "I love pickles", "My client is guilty!", "The prosecution is right", "I confess everything!"]
  }'
echo -e "\n"

# Cleanup
rm /tmp/storyboard.json