#!/bin/bash

API_URL="http://localhost:8000"

echo "Generating storyboard..."
curl -s -X POST "$API_URL/generate_storyboard"
sleep 3


echo -e "\nTesting interruption generation..."
curl -s -X POST "$API_URL/generate_interruption" \
  -H "Content-Type: application/json" \
  -d '{
    "storyboard": {
      "name": "John Smith",
      "accusation": "garden gnome theft",
      "how": "midnight raid",
      "when": "last Tuesday",
      "alibis": ["was at the movies"]
    },
    "current_text": "Your Honor, my client",
    "question": "Where was your client that night?",
    "difficulty": 7
  }'
sleep 3


echo -e "\nTesting judge question..."
curl -s -X POST "$API_URL/judge_question" \
  -H "Content-Type: application/json" \
  -d '{
    "attorney_responses": ["Your Honor, my client was at the movies"],
    "case_summary": {
      "name": "John Smith",
      "accusation": "garden gnome theft",
      "how": "midnight raid",
      "when": "last Tuesday",
      "alibis": ["was at the movies"]
    }
  }'
sleep 3


echo -e "\nTesting final verdict..."
curl -s -X POST "$API_URL/final_verdict" \
  -H "Content-Type: application/json" \
  -d '{
    "attorney_responses": ["Your Honor, my client was at the movies"],
    "case_summary": {
      "name": "John Smith",
      "accusation": "garden gnome theft",
      "how": "midnight raid",
      "when": "last Tuesday",
      "alibis": ["was at the movies"]
    }
  }'
sleep 3