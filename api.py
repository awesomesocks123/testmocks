import os
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pyperclip
import audioRecorder
import scrape
from app import get_llm_response, speak, add_context_to_history, load_context_from_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global state (similar to app.py)
cached_responses = []
current_user_input = ""

@app.route('/api/record', methods=['POST'])
def record_audio():
    """Record user audio input and return transcription"""
    try:
        transcription = audioRecorder.record()
        return jsonify({
            "success": True,
            "transcription": transcription
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/speak', methods=['POST'])
def text_to_speech():
    """Convert text to speech and play it"""
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "No text provided"}), 400
    
    try:
        speak(data['text'])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user input and get AI response"""
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"success": False, "error": "No message provided"}), 400
    
    try:
        user_input = data['message']
        ai_response = get_llm_response(user_input)
        
        # Cache the response
        global cached_responses
        cached_responses.append(ai_response)
        if len(cached_responses) > 5:
            cached_responses = cached_responses[-5:]
        
        return jsonify({
            "success": True,
            "response": ai_response
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/replay', methods=['GET'])
def replay_last():
    """Get the last AI response"""
    if not cached_responses:
        return jsonify({
            "success": False,
            "error": "No cached responses available"
        }), 404
    
    return jsonify({
        "success": True,
        "response": cached_responses[-1]
    })

@app.route('/api/cached-responses', methods=['GET'])
def get_cached():
    """Get all cached responses"""
    return jsonify({
        "success": True,
        "responses": cached_responses
    })

@app.route('/api/clipboard', methods=['POST'])
def add_clipboard():
    """Add clipboard content to context"""
    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content.strip():
            add_context_to_history(f"User added from clipboard:\n{clipboard_content}")
            return jsonify({
                "success": True,
                "message": "Clipboard content added to context"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Clipboard is empty"
            }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/leetcode', methods=['POST'])
def process_leetcode():
    """Process LeetCode problem URL"""
    data = request.json
    if not data or 'url' not in data:
        return jsonify({"success": False, "error": "No URL provided"}), 400
    
    try:
        url = data['url']
        slug = scrape.extract_slug(url)
        if not slug:
            return jsonify({"success": False, "error": "Invalid LeetCode URL"}), 400
        
        problem_data = scrape.fetch_problem_data(slug)
        scrape.save_to_txt(problem_data, slug)
        
        # Load the saved problem into context
        try:
            scraped_problems = load_context_from_file("scraped_problems.txt")
            add_context_to_history(scraped_problems)
            
            # Get initial AI response
            ai_response = get_llm_response("Introduce yourself and what problem you want me to solve today")
            
            # Cache the response
            global cached_responses
            cached_responses.append(ai_response)
            if len(cached_responses) > 5:
                cached_responses = cached_responses[-5:]
            
            return jsonify({
                "success": True,
                "problem": problem_data,
                "initial_response": ai_response
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Error loading problem into context: {str(e)}"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
